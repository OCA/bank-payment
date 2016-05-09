# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#              (C) 2011 - 2013 Therp BV (<http://therp.nl>).
#
#    All other contributions are (C) by their respective contributors
#
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp import netsvc
from openerp.tools.translate import _
from openerp.addons.decimal_precision import decimal_precision as dp
from openerp.addons.account_banking.parsers.models import (
    mem_bank_transaction as bt
)


class banking_import_transaction(orm.Model):
    _inherit = 'banking.import.transaction'

    def _match_payment_order(
            self, cr, uid, trans, log, order_type='payment', context=None):

        def equals_order_amount(payment_order, transferred_amount):
            if (not hasattr(payment_order, 'payment_order_type') or
                    payment_order.payment_order_type == 'payment'):
                sign = 1
            else:
                sign = -1
            total = payment_order.total + sign * transferred_amount
            return self.pool.get('res.currency').is_zero(
                cr, uid, trans.statement_line_id.statement_id.currency, total)

        payment_order_obj = self.pool.get('payment.order')

        order_ids = payment_order_obj.search(
            cr, uid, [('payment_order_type', '=', order_type),
                      ('state', '=', 'sent'),
                      ('date_sent', '<=', trans.execution_date),
                      ],
            limit=0, context=context)
        orders = payment_order_obj.browse(cr, uid, order_ids, context)
        candidates = [x for x in orders if
                      equals_order_amount(x, trans.statement_line_id.amount)]
        if len(candidates) > 0:
            # retrieve the common account_id, if any
            account_id = False
            transit_move_lines = candidates[0].line_ids[0].transit_move_line_id
            if transit_move_lines:
                for line in transit_move_lines.move_id.line_id:
                    if line.account_id.type == 'other':
                        account_id = line.account_id.id
                        break
            return dict(
                move_line_ids=False,
                match_type='payment_order',
                payment_order_ids=[x.id for x in candidates],
                account_id=account_id,
                partner_id=False,
                partner_bank_id=False,
                reference=False,
                type='general',
            )
        return False

    def _match_storno(
            self, cr, uid, trans, log, context=None):
        payment_line_obj = self.pool.get('payment.line')
        line_ids = payment_line_obj.search(
            cr, uid,
            [
                ('order_id.payment_order_type', '=', 'debit'),
                ('order_id.state', 'in', ['sent', 'done']),
                ('communication', '=', trans.reference)
            ],
            context=context)
        # stornos MUST have an exact match
        if len(line_ids) == 1:
            account_id = payment_line_obj.get_storno_account_id(
                cr, uid, line_ids[0], trans.statement_line_id.amount,
                trans.statement_id.currency, context=None)
            if account_id:
                return dict(
                    account_id=account_id,
                    match_type='storno',
                    payment_line_id=line_ids[0],
                    move_line_ids=False,
                    partner_id=False,
                    partner_bank_id=False,
                    reference=False,
                    type='customer',
                )
        # TODO log the reason why there is no result for transfers marked
        # as storno
        return False

    def _match_payment(self, cr, uid, trans, payment_lines,
                       partner_ids, bank_account_ids, log, linked_payments):
        '''
        Find the payment order belonging to this reference - if there is one
        This is the easiest part: when sending payments, the returned bank info
        should be identical to ours.
        This also means that we do not allow for multiple candidates.
        '''
        # TODO: Not sure what side effects are created when payments are done
        # for credited customer invoices, which will be matched later on too.

        def bank_match(account, partner_bank):
            """
            Returns whether a given account number is equivalent to a
            partner bank in the database. We simply call the search method,
            which checks IBAN, domestic and disregards from spaces in IBANs.

            :param account: string representation of a bank account number
            :param partner_bank: browse record of model res.partner.bank
            """
            return partner_bank.id in self.pool['res.partner.bank'].search(
                cr, uid, [('acc_number', '=', account)])

        digits = dp.get_precision('Account')(cr)[1]
        candidates = [
            line for line in payment_lines
            if (line.communication == trans.reference and
                round(line.amount, digits) == -round(
                    trans.statement_line_id.amount, digits) and
                bank_match(trans.remote_account, line.bank_id))
        ]
        if len(candidates) == 1:
            candidate = candidates[0]
            # Check cache to prevent multiple matching of a single payment
            if candidate.id not in linked_payments:
                linked_payments[candidate.id] = True
                move_info = self._get_move_info(
                    cr, uid, [candidate.move_line_id.id])
                move_info.update({
                    'match_type': 'payment',
                    'payment_line_id': candidate.id,
                })
                return move_info

        return False

    def _confirm_storno(
            self, cr, uid, transaction_id, context=None):
        """
        Creation of the reconciliation has been delegated to
        *a* direct debit module, to allow for various direct debit styles
        """
        payment_line_pool = self.pool.get('payment.line')
        statement_line_pool = self.pool.get('account.bank.statement.line')
        transaction = self.browse(cr, uid, transaction_id, context=context)
        if not transaction.payment_line_id:
            raise orm.except_orm(
                _("Cannot link with storno"),
                _("No direct debit order item"))
        reconcile_id = payment_line_pool.debit_storno(
            cr, uid,
            transaction.payment_line_id.id,
            transaction.statement_line_id.amount,
            transaction.statement_line_id.currency,
            transaction.storno_retry,
            context=context)
        statement_line_pool.write(
            cr, uid, transaction.statement_line_id.id,
            {'reconcile_id': reconcile_id}, context=context)
        transaction.refresh()

    def _confirm_payment_order(
            self, cr, uid, transaction_id, context=None):
        """
        Creation of the reconciliation has been delegated to
        *a* direct debit module, to allow for various direct debit styles
        """
        payment_order_obj = self.pool.get('payment.order')
        statement_line_pool = self.pool.get('account.bank.statement.line')
        transaction = self.browse(cr, uid, transaction_id, context=context)
        if not transaction.payment_order_id:
            raise orm.except_orm(
                _("Cannot reconcile"),
                _("Cannot reconcile: no direct debit order"))
        reconcile_id = payment_order_obj.debit_reconcile_transfer(
            cr, uid,
            transaction.payment_order_id.id,
            transaction.statement_line_id.amount,
            transaction.statement_line_id.currency,
            context=context)
        statement_line_pool.write(
            cr, uid, transaction.statement_line_id.id,
            {'reconcile_id': reconcile_id}, context=context)

    def _confirm_payment(
            self, cr, uid, transaction_id, context=None):
        """
        Do some housekeeping on the payment line
        then pass on to _reconcile_move
        """
        transaction = self.browse(cr, uid, transaction_id, context=context)
        payment_line_obj = self.pool.get('payment.line')
        payment_line_obj.write(
            cr, uid, transaction.payment_line_id.id,
            {
                'date_done': transaction.statement_line_id.date,
            }
        )
        self._confirm_move(cr, uid, transaction_id, context=context)
        # Check if the payment order is 'done'
        order_id = transaction.payment_line_id.order_id.id
        other_lines = payment_line_obj.search(
            cr, uid,
            [
                ('order_id', '=', order_id),
                ('date_done', '=', False),
            ],
            context=context)
        if not other_lines:
            wf_service = netsvc.LocalService('workflow')
            wf_service.trg_validate(
                uid, 'payment.order', order_id, 'done', cr)

    def _cancel_payment(
            self, cr, uid, transaction_id, context=None):
        """
        Do not support cancelling individual lines yet, because the workflow
        of the payment order does not support reopening.
        """
        raise orm.except_orm(
            _("Cannot unreconcile"),
            _("Cannot unreconcile: this operation is not yet supported for "
              "match type 'payment'"))

    def _cancel_payment_order(
            self, cr, uid, transaction_id, context=None):
        """
        """
        payment_order_obj = self.pool.get('payment.order')
        transaction = self.browse(cr, uid, transaction_id, context=context)
        if not transaction.payment_order_id:
            raise orm.except_orm(
                _("Cannot unreconcile"),
                _("Cannot unreconcile: no payment or direct debit order"))
        if not transaction.statement_line_id.reconcile_id:
            raise orm.except_orm(
                _("Cannot unreconcile"),
                _("Payment orders without transfer move lines cannot be "
                  "unreconciled this way"))
        return payment_order_obj.debit_unreconcile_transfer(
            cr, uid, transaction.payment_order_id.id,
            transaction.statement_line_id.reconcile_id.id,
            transaction.statement_line_id.amount,
            transaction.statement_line_id.currency)

    def _cancel_storno(
            self, cr, uid, transaction_id, context=None):
        """
        TODO: delegate unreconciliation to the direct debit module,
        to allow for various direct debit styles
        """
        payment_line_obj = self.pool.get('payment.line')
        reconcile_obj = self.pool.get('account.move.reconcile')
        transaction = self.browse(cr, uid, transaction_id, context=context)

        if not transaction.payment_line_id:
            raise orm.except_orm(
                _("Cannot cancel link with storno"),
                _("No direct debit order item"))
        if not transaction.payment_line_id.storno:
            raise orm.except_orm(
                _("Cannot cancel link with storno"),
                _("The direct debit order item is not marked for storno"))

        journal = transaction.statement_line_id.statement_id.journal_id
        if transaction.statement_line_id.amount >= 0:
            account_id = journal.default_credit_account_id.id
        else:
            account_id = journal.default_debit_account_id.id
        cancel_line = False
        move_lines = []
        for move in transaction.statement_line_id.move_ids:
            # There should usually be just one move, I think
            move_lines += move.line_id
        for line in move_lines:
            if line.account_id.id != account_id:
                cancel_line = line
                break
        if not cancel_line:
            raise orm.except_orm(
                _("Cannot cancel link with storno"),
                _("Line id not found"))
        reconcile = (cancel_line.reconcile_id or
                     cancel_line.reconcile_partial_id)
        lines_reconcile = reconcile.line_id or reconcile.line_partial_ids
        if len(lines_reconcile) < 3:
            # delete the full reconciliation
            reconcile_obj.unlink(cr, uid, reconcile.id, context)
        else:
            # we are left with a partial reconciliation
            reconcile_obj.write(
                cr, uid, reconcile.id,
                {'line_partial_ids':
                 [(6, 0, [x.id for x in lines_reconcile
                          if x.id != cancel_line.id])],
                 'line_id': [(6, 0, [])],
                 }, context)
        # redo the original payment line reconciliation with the invoice
        payment_line_obj.write(
            cr, uid, transaction.payment_line_id.id,
            {'storno': False}, context)
        payment_line_obj.debit_reconcile(
            cr, uid, transaction.payment_line_id.id, context)

    _columns = {
        'payment_order_ids': fields.many2many(
            'payment.order', 'banking_transaction_payment_order_rel',
            'order_id', 'transaction_id', 'Payment orders'),
        'payment_order_id': fields.many2one(
            'payment.order', 'Payment order to reconcile'),
        'payment_line_id': fields.many2one('payment.line', 'Payment line'),
    }

    def _get_match_multi(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        res = super(banking_import_transaction, self)._get_match_multi(
            cr, uid, ids, name, args, context=context)
        for transaction in self.browse(cr, uid, ids, context):
            if transaction.match_type == 'payment_order':
                if (transaction.payment_order_ids and not
                        transaction.payment_order_id):
                    res[transaction.id] = True
        return res

    def clear_and_write(self, cr, uid, ids, vals=None, context=None):
        write_vals = {
            'payment_line_id': False,
            'payment_order_id': False,
            'payment_order_ids': [(6, 0, [])],
        }
        write_vals.update(vals or {})
        return super(banking_import_transaction, self).clear_and_write(
            cr, uid, ids, vals=vals, context=context)

    def move_info2values(self, move_info):
        vals = super(banking_import_transaction, self).move_info2values(
            move_info)
        vals['payment_line_id'] = move_info.get('payment_line_id', False)
        vals['payment_order_ids'] = [
            (6, 0, move_info.get('payment_order_ids') or [])]
        vals['payment_order_id'] = (
            move_info.get('payment_order_ids', False) and
            len(move_info['payment_order_ids']) == 1 and
            move_info['payment_order_ids'][0]
        )
        return vals

    def hook_match_payment(self, cr, uid, transaction, log, context=None):
        """
        Called from match() in the core module.
        Match payment batches, direct debit orders and stornos
        """
        move_info = False
        if transaction.type == bt.PAYMENT_BATCH:
            move_info = self._match_payment_order(
                cr, uid, transaction, log,
                order_type='payment', context=context)
        elif transaction.type == bt.DIRECT_DEBIT:
            move_info = self._match_payment_order(
                cr, uid, transaction, log,
                order_type='debit', context=context)
        elif transaction.type == bt.STORNO:
            move_info = self._match_storno(
                cr, uid, transaction, log,
                context=context)
        return move_info

    def __init__(self, pool, cr):
        """
        Updating the function maps to handle the match types that this
        module adds.
        """
        super(banking_import_transaction, self).__init__(pool, cr)

        self.confirm_map.update({
            'storno': banking_import_transaction._confirm_storno,
            'payment_order': banking_import_transaction._confirm_payment_order,
            'payment': banking_import_transaction._confirm_payment,
            'payment_order_manual': (
                banking_import_transaction._confirm_payment_order),
            'payment_manual': banking_import_transaction._confirm_payment,
        })

        self.cancel_map.update({
            'storno': banking_import_transaction._cancel_storno,
            'payment_order': banking_import_transaction._cancel_payment_order,
            'payment': banking_import_transaction._cancel_payment,
            'payment_order_manual': (
                banking_import_transaction._cancel_payment_order),
            'payment_manual': banking_import_transaction._cancel_payment,
        })
