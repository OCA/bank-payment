# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#                  Contributions by Kaspars Vilkens (KNdati):
#                  lenghty discussions, bugreports and bugfixes
#    Refractoring (C) 2011 Therp BV (<http://therp.nl>).
#                 (C) 2011 Smile (<http://smile.fr>).
#
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
import time
import netsvc
import base64
import datetime
from tools import config
from tools.translate import _
from parsers import models
from parsers.convert import *
# from account_banking.struct import struct
from account_banking import sepa
from wizard.banktools import *
import decimal_precision as dp

bt = models.mem_bank_transaction

class banking_import_transaction(osv.osv):
    """ orm representation of mem_bank_transaction() for interactive and posthoc
    configuration of reconciliation in the bank statement view.

    Possible refractoring in OpenERP 6.1:
    merge with bank_statement_line, using sparse fields

    """
    _name = 'banking.import.transaction'
    _description = 'Bank import transaction'
    _rec_name = 'transaction'

    # This variable is used to match supplier invoices with an invoice date after
    # the real payment date. This can occur with online transactions (web shops).
    # TODO: Convert this to a proper configuration variable
    payment_window = datetime.timedelta(days=10)

    def _match_costs(self, cr, uid, trans, period_id, account_info, log):
        '''
        Get or create a costs invoice for the bank and return it with
        the payment as seen in the transaction (when not already done).
        '''
        if not account_info.costs_account_id:
            return []

        digits = dp.get_precision('Account')(cr)[1]
        amount = round(abs(trans.transferred_amount), digits)
        # Make sure to be able to pinpoint our costs invoice for later
        # matching
        reference = '%s.%s: %s' % (trans.statement, trans.transaction, trans.reference)

        # search supplier invoice
        invoice_obj = self.pool.get('account.invoice')
        invoice_ids = invoice_obj.search(cr, uid, [
            '&',
            ('type', '=', 'in_invoice'),
            ('partner_id', '=', account_info.bank_partner_id.id),
            ('company_id', '=', account_info.company_id.id),
            ('date_invoice', '=', trans.effective_date),
            ('reference', '=', reference),
            ('amount_total', '=', amount),
            ]
        )
        if invoice_ids and len(invoice_ids) == 1:
            invoice = invoice_obj.browse(cr, uid, invoice_ids)[0]
        elif not invoice_ids:
            # create supplier invoice
            partner_obj = self.pool.get('res.partner')
            invoice_lines = [(0,0,dict(
                amount = 1,
                price_unit = amount,
                name = trans.message or trans.reference,
                account_id = account_info.costs_account_id.id
            ))]
            invoice_address_id = partner_obj.address_get(
                cr, uid, [account_info.bank_partner_id.id], ['invoice']
            )
            invoice_id = invoice_obj.create(cr, uid, dict(
                type = 'in_invoice',
                company_id = account_info.company_id.id,
                partner_id = account_info.bank_partner_id.id,
                address_invoice_id = invoice_address_id['invoice'],
                period_id = period_id,
                journal_id = account_info.invoice_journal_id.id,
                account_id = account_info.bank_partner_id.property_account_payable.id,
                date_invoice = trans.effective_date,
                reference_type = 'none',
                reference = reference,
                name = trans.reference or trans.message,
                check_total = amount,
                invoice_line = invoice_lines,
            ))
            invoice = invoice_obj.browse(cr, uid, invoice_id)
            # Create workflow
            invoice_obj.button_compute(cr, uid, [invoice_id], 
                                       {'type': 'in_invoice'}, set_total=True)
            wf_service = netsvc.LocalService('workflow')
            # Move to state 'open'
            wf_service.trg_validate(uid, 'account.invoice', invoice.id,
                                    'invoice_open', cr)

        # return move_lines to mix with the rest
        return [x for x in invoice.move_id.line_id if x.account_id.reconcile]

    def _match_debit_order(
        self, cr, uid, trans, log, context=None):

        def is_zero(total):
            return self.pool.get('res.currency').is_zero(
                cr, uid, trans.statement_id.currency, total)

        payment_order_obj = self.pool.get('payment.order')
        order_ids = payment_order_obj.search(
            cr, uid, [('payment_order_type', '=', 'debit'),
                      ('state', '=', 'sent'),
                      ('date_sent', '<=', str2date(trans.execution_date,
                                                   '%Y-%m-%d'))
                      ],
            limit=0, context=context)
        orders = payment_order_obj.browse(cr, uid, order_ids, context)
        candidates = [x for x in orders if
                      is_zero(x.total - trans.transferred_amount)]
        if len(candidates) > 0:
            # retrieve the common account_id, if any
            account_id = False
            for line in candidates[0].line_ids[0].debit_move_line_id.move_id.line_id:
                if line.account_id.type == 'other':
                    account_id = line.account_id.id
                    break
            return dict(
                move_line_ids = False,
                match_type = 'payment_order',
                payment_order_ids = [x.id for x in candidates],
                account_id = account_id,
                partner_id = False,
                partner_bank_id = False,
                reference = False,
                type='general',
                )
        return False

    def _match_invoice(self, cr, uid, trans, move_lines,
                       partner_ids, bank_account_ids,
                       log, linked_invoices,
                       context=None):
        '''
        Find the invoice belonging to this reference - if there is one
        Use the sales journal to check.

        Challenges we're facing:
            1. The sending or receiving party is not necessarily the same as the
               partner the payment relates to.
            2. References can be messed up during manual encoding and inexact
               matching can link the wrong invoices.
            3. Amounts can or can not match the expected amount.
            4. Multiple invoices can be paid in one transaction.
            .. There are countless more, but these we'll try to address.

        Assumptions for matching:
            1. There are no payments for invoices not sent. These are dealt with
               later on.
            2. Debit amounts are either customer invoices or credited supplier
               invoices.
            3. Credit amounts are either supplier invoices or credited customer
               invoices.
            4. Payments are either below expected amount or only slightly above
               (abs).
            5. Payments from partners that are matched, pay their own invoices.
        
        Worst case scenario:
            1. No match was made.
               No harm done. Proceed with manual matching as usual.
            2. The wrong match was made.
               Statements are encoded in draft. You will have the opportunity to
               manually correct the wrong assumptions. 

        TODO: REVISE THIS DOC
        #Return values:
        # old_trans: this function can modify and rebrowse the modified
        # transaction.
        # move_info: the move_line information belonging to the matched
        #               invoice
        #    new_trans: the new transaction when the current one was split.
        #    This can happen when multiple invoices were paid with a single
        #    bank transaction.
        '''

        def eyecatcher(invoice):
            '''
            Return the eyecatcher for an invoice
            '''
            return invoice.type.startswith('in_') and invoice.name or \
                    invoice.number

        def has_id_match(invoice, ref, msg):
            '''
            Aid for debugging - way more comprehensible than complex
            comprehension filters ;-)

            Match on ID of invoice (reference, name or number, whatever
            available and sensible)
            '''
            if invoice.reference:
                # Reference always comes first, as it is manually set for a
                # reason.
                iref = invoice.reference.upper()
                if iref in ref or iref in msg:
                    return True
            if invoice.type.startswith('in_'):
                # Internal numbering, no likely match on number
                if invoice.name:
                    iname = invoice.name.upper()
                    if iname in ref or iname in msg:
                        return True
            elif invoice.type.startswith('out_'):
                # External id's possible and likely
                inum = invoice.number.upper()
                if inum in ref or inum in msg:
                    return True

            return False

        def _cached(move_line):
            # Disabled, we allow for multiple matches in
            # the interactive wizard
            return False

            '''Check if the move_line has been cached'''
            return move_line.id in linked_invoices

        def _cache(move_line, remaining=0.0):
            '''Cache the move_line'''
            linked_invoices[move_line.id] = remaining

        def _remaining(move_line):
            '''Return the remaining amount for a previously matched move_line
            '''
            return linked_invoices[move_line.id]

        def _sign(invoice):
            '''Return the direction of an invoice'''
            return {'in_invoice': -1, 
                    'in_refund': 1,
                    'out_invoice': 1,
                    'out_refund': -1
                   }[invoice.type]

        def is_zero(move_line, total):
            return self.pool.get('res.currency').is_zero(
                cr, uid, trans.statement_id.currency, total)

        digits = dp.get_precision('Account')(cr)[1]
        partial = False

        # Disabled splitting transactions for now
        # TODO allow splitting in the interactive wizard
        allow_splitting = False

        # Search invoice on partner
        if partner_ids:
            candidates = [
                x for x in move_lines
                if x.partner_id.id in partner_ids and
                (str2date(x.date, '%Y-%m-%d') <=
                 (str2date(trans.execution_date, '%Y-%m-%d') +
                  self.payment_window))
                and (not _cached(x) or _remaining(x))
                ]
        else:
            candidates = []

        # Next on reference/invoice number. Mind that this uses the invoice
        # itself, as the move_line references have been fiddled with on invoice
        # creation. This also enables us to search for the invoice number in the
        # reference instead of the other way around, as most human interventions
        # *add* text.
        if len(candidates) > 1 or not candidates:
            ref = trans.reference.upper()
            msg = trans.message.upper()
            # The manual usage of the sales journal creates moves that
            # are not tied to invoices. Thanks to Stefan Rijnhart for
            # reporting this.
            candidates = [
                x for x in candidates or move_lines 
                if (x.invoice and has_id_match(x.invoice, ref, msg) and
                    str2date(x.invoice.date_invoice, '%Y-%m-%d') <=
                    (str2date(trans.execution_date, '%Y-%m-%d') +
                     self.payment_window)
                    and (not _cached(x) or _remaining(x)))
                ]

        # Match on amount expected. Limit this kind of search to known
        # partners.
        if not candidates and partner_ids:
            candidates = [
                    x for x in move_lines 
                    if (is_zero(x.move_id, ((x.debit or 0.0) - (x.credit or 0.0)) -
                                trans.transferred_amount)
                        and str2date(x.date, '%Y-%m-%d') <=
                        (str2date(trans.execution_date, '%Y-%m-%d')  +
                         self.payment_window)
                        and (not _cached(x) or _remaining(x)))
                    ]

        move_line = False

        if candidates and len(candidates) > 0:
            # Now a possible selection of invoices has been found, check the
            # amounts expected and received.
            #
            # TODO: currency coercing
            best = [x for x in candidates
                    if (is_zero(x.move_id, ((x.debit or 0.0) - (x.credit or 0.0)) -
                                trans.transferred_amount)
                        and str2date(x.date, '%Y-%m-%d') <=
                        (str2date(trans.execution_date, '%Y-%m-%d') +
                         self.payment_window))
                   ]
            if len(best) == 1:
                # Exact match
                move_line = best[0]
                invoice = move_line.invoice
                if _cached(move_line):
                    partial = True
                    expected = _remaining(move_line)
                else:
                    _cache(move_line)

            elif len(candidates) > 1:
                # Before giving up, check cache for catching duplicate
                # transfers first
                paid = [x for x in move_lines 
                        if x.invoice and has_id_match(x.invoice, ref, msg)
                            and str2date(x.invoice.date_invoice, '%Y-%m-%d')
                                <= str2date(trans.execution_date, '%Y-%m-%d')
                            and (_cached(x) and not _remaining(x))
                       ]
                if paid:
                    log.append(
                        _('Unable to link transaction id %(trans)s '
                          '(ref: %(ref)s) to invoice: '
                          'invoice %(invoice)s was already paid') % {
                              'trans': '%s.%s' % (trans.statement, trans.transaction),
                              'ref': trans.reference,
                              'invoice': eyecatcher(paid[0].invoice)
                          })
                else:
                    # Multiple matches
                    # TODO select best bank account in this case
                    return (trans, self._get_move_info(
                            cr, uid, [x.id for x in candidates]),
                            False)
                move_line = False
                partial = False

            elif len(candidates) == 1:
                # Mismatch in amounts
                move_line = candidates[0]
                invoice = move_line.invoice
                expected = round(_sign(invoice) * invoice.residual, digits)
                partial = True

            trans2 = None
            if move_line and partial:
                found = round(trans.transferred_amount, digits)
                if abs(expected) == abs(found):
                    partial = False
                    # Last partial payment will not flag invoice paid without
                    # manual assistence
                    # Stefan: disabled this here for the interactive method
                    # Handled this with proper handling of partial reconciliation 
                    #   and the workflow service
                    # invoice_obj = self.pool.get('account.invoice')
                    # invoice_obj.write(cr, uid, [invoice.id], {
                    #     'state': 'paid'
                    #  })
                elif abs(expected) > abs(found):
                    # Partial payment, reuse invoice
                    _cache(move_line, expected - found)
                elif abs(expected) < abs(found) and allow_splitting:
                    # Possible combined payments, need to split transaction to
                    # verify
                    _cache(move_line)
                    trans2 = self.copy(
                    cr, uid, trans.id, 
                    dict(
                            transferred_amount = trans.transferred_amount - expected,
                            transaction = trans.transaction + 'b',
                            parent_id = trans.id,
                            ), context=context)
                    # update the current record
                    self.write(cr, uid, trans.id, dict(
                            transferred_amount = expected,
                            transaction = trans.transaction + 'a',
                            ), context)
                    # rebrowse the current record after writing
                    trans = self.browse(cr, uid, trans.id, context=context)
            if move_line:
                account_ids = [
                    x.id for x in bank_account_ids 
                    if x.partner_id.id == move_line.partner_id.id
                    ]
                
            return (trans, self._get_move_info(
                    cr, uid, [move_line.id],
                    account_ids and account_ids[0] or False),
                    trans2)

        return trans, False, False

    def _do_move_reconcile(
        self, cr, uid, move_line_ids, currency, amount, context=None):
        """
        Prepare a reconciliation for a bank transaction of the given
        amount. The caller MUST add the move line associated with the
        bank transaction to the returned reconciliation resource.

        If adding the amount does not make the total add up,
        prepare a partial reconciliation. An existing reconciliation on
        the move lines will be taken into account.

        :param move_line_ids: List of ids. This will usually be the move
        line of an associated invoice or payment, plus optionally the
        move line of a writeoff. 
        :param currency: A res.currency *browse* object to perform math
        operations on the amounts.
        :param amount: the amount of the bank transaction. Amount < 0 in
        case of a credit move on the bank account.
        """
        move_line_obj = self.pool.get('account.move.line')
        reconcile_obj = self.pool.get('account.move.reconcile')
        is_zero = lambda amount: self.pool.get('res.currency').is_zero(
            cr, uid, currency, amount)
        move_lines = move_line_obj.browse(cr, uid, move_line_ids, context=context)
        reconcile = False
        for move_line in move_lines:
            if move_line.reconcile_id:
                raise osv.except_osv(
                    _('Entry is already reconciled'),
                    _("You cannot reconcile the bank transaction with this entry, " +
                      "it is already reconciled")
                    )
            if move_line.reconcile_partial_id:
                if reconcile and reconcile.id != move_line.reconcile_partial_id.id:
                    raise osv.except_osv(
                        _('Cannot reconcile'),
                        _('Move lines are already partially reconciled, ' +
                          'but not with each other.'))
                reconcile = move_line.reconcile_partial_id
        line_ids = list(set(move_line_ids + (
                    [x.id for x in reconcile and ( # reconcile.line_id or 
                            reconcile.line_partial_ids) or []])))
        if not reconcile:
            reconcile_id = reconcile_obj.create(
                cr, uid, {'type': 'auto' }, context=context)
            reconcile = reconcile_obj.browse(cr, uid, reconcile_id, context=context)
        full = is_zero(
            move_line_obj.get_balance(cr, uid, line_ids) - amount)
        # we should not have to check whether there is a surplus writeoff
        # as any surplus amount *should* have been split off in the matching routine
        if full:
            line_partial_ids = []
        else:
            line_partial_ids = line_ids[:]
            line_ids = []
        reconcile_obj.write(
            cr, uid, reconcile_id, 
            { 'line_id': [(6, 0, line_ids)],
              'line_partial_ids': [(6, 0, line_partial_ids)],
              }, context=context)
        return reconcile_id

    def _do_move_unreconcile(self, cr, uid, move_line_ids, currency, context=None):
        """
        Undo a reconciliation, removing the given move line ids. If no
        meaningful (partial) reconciliation remains, delete it.

        :param move_line_ids: List of ids. This will usually be the move
        line of an associated invoice or payment, plus optionally the
        move line of a writeoff. 
        :param currency: A res.currency *browse* object to perform math
        operations on the amounts.
        """

        move_line_obj = self.pool.get('account.move.line')
        reconcile_obj = self.pool.get('account.move.reconcile')
        is_zero = lambda amount: self.pool.get('res.currency').is_zero(
            cr, uid, currency, amount)
        move_lines = move_line_obj.browse(cr, uid, move_line_ids, context=context)
        reconcile = move_lines[0].reconcile_id or move_lines[0].reconcile_partial_id
        line_ids = [x.id for x in reconcile.line_id or reconcile.line_partial_ids]
        for move_line_id in move_line_ids:
            line_ids.remove(move_line_id)
        if len(line_ids) > 1:
            full = is_zero(move_line_obj.get_balance(cr, uid, line_ids))
            if full:
                line_partial_ids = []
            else:
                line_partial_ids = line_ids.copy()
                line_ids = []
            reconcile_obj.write(
                cr, uid, reconcile.id,
                { 'line_partial_ids': [(6, 0, line_ids)],
                  'line_id': [(6, 0, line_partial_ids)],
                  }, context=context)
        else:
            reconcile_obj.unlink(cr, uid, reconcile.id, context=context)
        for move_line in move_lines:
            if move_line.invoice:
                # reopening the invoice
                netsvc.LocalService('workflow').trg_validate(
                    uid, 'account.invoice', move_line.invoice.id, 'undo_paid', cr)
        return True

    def _reconcile_move(
        self, cr, uid, transaction_id, context=None):
        transaction = self.browse(cr, uid, transaction_id, context=context)
        if not transaction.move_line_id:
            if transaction.match_type == 'invoice':
                raise osv.except_osv(
                    _("Cannot link transaction %s with invoice") %
                    transaction.statement_line_id.name,
                    (transaction.invoice_ids and
                     (_("Please select one of the matches in transaction %s.%s") or
                     _("No match found for transaction %s.%s")) % (
                            transaction.statement_line_id.statement_id.name,
                            transaction.statement_line_id.name
                     )))
            else:
                raise osv.except_osv(
                    _("Cannot link transaction %s with accounting entry") %
                    transaction.statement_line_id.name,
                    (transaction.move_line_ids and
                     (_("Please select one of the matches in transaction %s.%s") or
                     _("No match found for transaction %s.%s")) % (
                            transaction.statement_line_id.statement_id.name,
                            transaction.statement_line_id.name
                     )))
        currency = transaction.statement_line_id.statement_id.currency
        line_ids = [transaction.move_line_id.id]
        if transaction.writeoff_move_line_id:
            line_ids.append(transaction.writeoff_move_line_id.id)
        reconcile_id = self._do_move_reconcile(
            cr, uid, line_ids, currency,
            transaction.transferred_amount, context=context)
        return reconcile_id

    def _reconcile_storno(
        self, cr, uid, transaction_id, context=None):
        """
        Creation of the reconciliation has been delegated to
        *a* direct debit module, to allow for various direct debit styles
        """
        payment_line_obj = self.pool.get('payment.line')
        transaction = self.browse(cr, uid, transaction_id, context=context)
        if not transaction.payment_line_id:
            raise osv.except_osv(
                _("Cannot link with storno"),
                _("No direct debit order item"))
        return payment_line_obj.debit_storno(
            cr, uid,
            transaction.payment_line_id.id, 
            transaction.statement_line_id.amount,
            transaction.statement_line_id.currency,
            transaction.storno_retry,
            context=context)

    def _reconcile_payment_order(
        self, cr, uid, transaction_id, context=None):
        """
        Creation of the reconciliation has been delegated to
        *a* direct debit module, to allow for various direct debit styles
        """
        payment_order_obj = self.pool.get('payment.order')
        transaction = self.browse(cr, uid, transaction_id, context=context)
        if not transaction.payment_order_id:
            raise osv.except_osv(
                _("Cannot reconcile"),
                _("Cannot reconcile: no direct debit order"))
        if transaction.payment_order_id.payment_order_type != 'debit':
            raise osv.except_osv(
                _("Cannot reconcile"),
                _("Reconcile payment order not implemented"))
        return payment_order_obj.debit_reconcile_transfer(
            cr, uid,
            transaction.payment_order_id.id,
            transaction.statement_line_id.amount,
            transaction.statement_line_id.currency,
            context=context)

    def _reconcile_payment(
        self, cr, uid, transaction_id, context=None):
        """
        Do some housekeeping on the payment line
        then pass on to _reconcile_move
        """
        transaction = self.browse(cr, uid, transaction_id, context=context)
        payment_line_obj = self.pool.get('payment.line')
        payment_line_obj.write(
            cr, uid, transaction.payment_line_id.id, {
                'export_state': 'done',
                'date_done': transaction.effective_date,
                }
            )
        return self._reconcile_move(cr, uid, transaction_id, context=context)
        
    def _cancel_payment(
        self, cr, uid, transaction_id, context=None):
        raise osv.except_osv(
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
            raise osv.except_osv(
                _("Cannot unreconcile"),
                _("Cannot unreconcile: no direct debit order"))
        if transaction.payment_order_id.payment_order_type != 'debit':
            raise osv.except_osv(
                _("Cannot unreconcile"),
                _("Unreconcile payment order not implemented"))
        return payment_order_obj.debit_unreconcile_transfer(
            cr, uid, transaction.payment_order_id.id,
            transaction.statement_line_id.reconcile_id.id,
            transaction.statement_line_id.amount,
            transaction.statement_line_id.currency)

    def _cancel_move(
        self, cr, uid, transaction_id, context=None):
        statement_line_obj = self.pool.get('account.bank.statement.line')
        transaction = self.browse(cr, uid, transaction_id, context=context)
        move_line_id = transaction.move_line_id.id
        currency = transaction.statement_line_id.statement_id.currency
        line_ids = [transaction.move_line_id.id]
        if transaction.writeoff_move_line_id:
            line_ids.append(transaction.writeoff_move_line_id.id)
        self._do_move_unreconcile(
            cr, uid, line_ids, currency, context=context)
        statement_line_obj.write(
            cr, uid, transaction.statement_line_id.id,
            {'reconcile_id': False}, context=context)
        return True

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
            raise osv.except_osv(
                _("Cannot cancel link with storno"),
                _("No direct debit order item"))
        if not transaction.payment_line_id.storno:
            raise osv.except_osv(
                _("Cannot cancel link with storno"),
                _("The direct debit order item is not marked for storno"))

        journal = transaction.statement_line_id.statement_id.journal_id
        if transaction.statement_line_id.amount >= 0:
            account_id = journal.default_credit_account_id.id
        else:
            account_id = journal.default_debit_account_id.id
        cancel_line = False
        for line in transaction.statement_line_id.move_id.line_id:
            if line.account_id.id != account_id:
                cancel_line = line
                break
        if not cancel_line: # debug
            raise osv.except_osv(
                _("Cannot cancel link with storno"),
                _("Line id not found"))
        reconcile = cancel_line.reconcile_id or cancel_line.reconcile_partial_id
        lines_reconcile = reconcile.line_id or reconcile.line_partial_ids
        if len(lines_reconcile) < 3:
            # delete the full reconciliation
            reconcile_obj.unlink(cr, uid, reconcile.id, context)
        else:
            # we are left with a partial reconciliation
            reconcile_obj.write(
                cr, uid, reconcile.id, 
                {'line_partial_ids': 
                 [(6, 0, [x.id for x in lines_reconcile if x.id != cancel_line.id])],
                 'line_id': [(6, 0, [])],
                 }, context)
        # redo the original payment line reconciliation with the invoice
        payment_line_obj.write(
            cr, uid, transaction.payment_line_id.id, 
            {'storno': False}, context)
        payment_line_obj.debit_reconcile(
            cr, uid, transaction.payment_line_id.id, context)

    cancel_map = {
        'storno': _cancel_storno,
        'invoice': _cancel_move,
        'manual': _cancel_move,
        'move': _cancel_move,
        'payment_order': _cancel_payment_order,
        'payment': _cancel_payment,
        }
    def cancel(self, cr, uid, ids, context=None):
        if ids and isinstance(ids, (int, float)):
            ids = [ids]
        move_obj = self.pool.get('account.move')
        for transaction in self.browse(cr, uid, ids, context):
            if not transaction.match_type:
                continue
            if transaction.match_type not in self.cancel_map:
                raise osv.except_osv(
                    _("Cannot cancel type %s" % transaction.match_type),
                    _("No method found to cancel this type"))
            self.cancel_map[transaction.match_type](
                self, cr, uid, transaction.id, context)
            # clear up the writeoff move
            if transaction.writeoff_move_line_id:
                move_obj.button_cancel(
                    cr, uid, [transaction.writeoff_move_line_id.move_id.id],
                    context=context)
                move_obj.unlink(
                    cr, uid, [transaction.writeoff_move_line_id.move_id.id],
                    context=context)
        return True

    reconcile_map = {
        'storno': _reconcile_storno,
        'invoice': _reconcile_move,
        'manual': _reconcile_move,
        'payment_order': _reconcile_payment_order,
        'payment': _reconcile_payment,
        'move': _reconcile_move,
        }
    def reconcile(self, cr, uid, ids, context=None):
        if ids and isinstance(ids, (int, float)):
            ids = [ids]
        for transaction in self.browse(cr, uid, ids, context):
            if not transaction.match_type:
                continue
            if transaction.match_type not in self.reconcile_map:
                raise osv.except_osv(
                    _("Cannot reconcile"),
                    _("Cannot reconcile type %s. No method found to " +
                      "reconcile this type") %
                    transaction.match_type
                    )
            if (transaction.residual and transaction.writeoff_account_id):
                if transaction.match_type not in ('invoice', 'move', 'manual'):
                    raise osv.except_osv(
                        _("Cannot reconcile"),
                        _("Bank transaction %s: write off not implemented for " +
                          "this match type.") %
                        transaction.statement_line_id.name
                        )
                self._generate_writeoff_move(
                    cr, uid, transaction.id, context=context)
            # run the method that is appropriate for this match type
            reconcile_id = self.reconcile_map[transaction.match_type](
                self, cr, uid, transaction.id, context)
            self.pool.get('account.bank.statement.line').write(
                cr, uid, transaction.statement_line_id.id, 
                {'reconcile_id': reconcile_id}, context=context)

        # TODO
        # update the statement line bank account reference
        # as follows (from _match_invoice)
        
        """
        account_ids = [
        x.id for x in bank_account_ids 
        if x.partner_id.id == move_line.partner_id.id
        ][0]
        """
        return True

    
    def _generate_writeoff_move(self, cr, uid, ids, context):
        if ids and isinstance(ids, (int, float)):
            ids = [ids]
        move_line_obj = self.pool.get('account.move.line')
        move_obj = self.pool.get('account.move')
        for trans in self.browse(cr, uid, ids, context=context):
            periods = self.pool.get('account.period').find(
                cr, uid, trans.statement_line_id.date)
            period_id =  periods and periods[0] or False
            move_id = move_obj.create(cr, uid, {
                    'journal_id': trans.writeoff_journal_id.id,
                    'period_id': period_id,
                    'date': trans.statement_line_id.date,
                    'name': '(write-off) %s' % (
                        trans.move_line_id.move_id.name or '')
                    }, context=context)
            writeoff_debit = False
            writeoff_credit = False
            if trans.statement_line_id.amount > 0:
                if trans.residual > 0:
                    writeoff_debit = trans.residual
                else:
                    writeoff_credit = - trans.residual
            else:
                if trans.residual > 0:
                    writeoff_credit = trans.residual
                else:
                    writeoff_debit = - trans.residual
            vals = {
                'name': trans.statement_line_id.name,
                'date': trans.statement_line_id.date,
                'ref': trans.statement_line_id.ref,
                'move_id': move_id,
                'partner_id': (trans.statement_line_id.partner_id and
                               trans.statement_line_id.partner_id.id or False),
                'account_id': trans.statement_line_id.account_id.id,
                'credit': writeoff_debit,
                'debit': writeoff_credit,
                'journal_id': trans.writeoff_journal_id.id,
                'period_id': period_id,
                'currency_id': trans.statement_line_id.statement_id.currency.id,
                }
            move_line_id = move_line_obj.create(
                cr, uid, vals, context=context)
            self.write(
                cr, uid, trans.id, 
                {'writeoff_move_line_id': move_line_id}, context=context)
            vals.update({
                    'account_id': trans.writeoff_account_id.id,
                    'credit': writeoff_credit,
                    'debit': writeoff_debit,
                    })
            move_line_obj.create(
                cr, uid, vals, context=context)
            move_obj.post(
                cr, uid, [move_id], context=context)

    def _match_storno(
        self, cr, uid, trans, log, context=None):
        payment_line_obj = self.pool.get('payment.line')
        line_ids = payment_line_obj.search(
            cr, uid, [
                ('order_id.payment_order_type', '=', 'debit'),
                ('order_id.state', 'in', ['sent', 'done']),
                ('communication', '=', trans.reference)
                ], context=context)
        # stornos MUST have an exact match
        if len(line_ids) == 1:
            account_id = payment_line_obj.get_storno_account_id(
                cr, uid, line_ids[0], trans.transferred_amount,
                trans.statement_id.currency, context=None)
            if account_id:
                return dict(
                    account_id = account_id,
                    match_type = 'storno',
                    payment_line_id = line_ids[0],
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
        digits = dp.get_precision('Account')(cr)[1]
        candidates = [x for x in payment_lines
                      if x.communication == trans.reference 
                      and round(x.amount, digits) == -round(trans.transferred_amount, digits)
                      and trans.remote_account in (x.bank_id.acc_number,
                                                   x.bank_id.iban)
                     ]
        if len(candidates) == 1:
            candidate = candidates[0]
            # Check cache to prevent multiple matching of a single payment
            if candidate.id not in linked_payments:
                linked_payments[candidate.id] = True
                move_info = self._get_move_info(cr, uid, [candidate.move_line_id.id])
                move_info.update({
                        'match_type': 'payment',
                        'payment_line_id': candidate.id,
                        })
                return move_info

        return False

    signal_duplicate_keys = [
        # does not include float values
        # such as transferred_amount
        'execution_date', 'local_account', 'remote_account',
        'remote_owner', 'reference', 'message',
        ]

    def create(self, cr, uid, vals, context=None):
        res = super(banking_import_transaction, self).create(
            cr, uid, vals, context)
        if res:
            me = self.browse(cr, uid, res, context)
            search_vals = [(key, '=', me[key]) 
                           for key in self.signal_duplicate_keys]
            ids = self.search(cr, uid, search_vals, context=context)
            dupes = []
            # Test for transferred_amount seperately
            # due to float representation and rounding difficulties
            for trans in self.browse(cr, uid, ids, context=context):
                if self.pool.get('res.currency').is_zero(
                    cr, uid, 
                    trans.statement_id.currency,
                    me['transferred_amount'] - trans.transferred_amount):
                    dupes.append(trans.id)
            if len(dupes) < 1:
                raise osv.except_osv(_('Cannot check for duplicate'),
                               _("Cannot check for duplicate. "
                                 "I can't find myself."))
            if len(dupes) > 1:
                self.write(
                    cr, uid, res, {'duplicate': True}, context=context)
        return res

    def split_off(self, cr, uid, res_id, amount, context=None):
        # todo. Inherit the duplicate marker from res_id
        pass

    def combine(self, cr, uid, ids, context=None):
        # todo. Check equivalence of primary key
        pass
    
    def _get_move_info(self, cr, uid, move_line_ids, partner_bank_id=False,
                       partial=False, match_type = False):
        type_map = {
            'out_invoice': 'customer',
            'in_invoice': 'supplier',
            'out_refund': 'customer',
            'in_refund': 'supplier',
        }
        retval = {'partner_id': False,
                  'partner_bank_id': partner_bank_id,
                  'reference': False,
                  'type': 'general',
                  'move_line_ids': move_line_ids,
                  'match_type': match_type,
                  'account_id': False,
                  }
        move_lines = self.pool.get('account.move.line').browse(cr, uid, move_line_ids)
        for move_line in move_lines:
            if move_line.partner_id:
                if retval['partner_id']:
                    if retval['partner_id'] != move_line.partner_id.id:
                        retval['partner_id'] = False
                        break
                else:
                    retval['partner_id'] = move_line.partner_id.id
            else:
                if retval['partner_id']: 
                    retval['partner_id'] = False
                    break
        for move_line in move_lines:
            if move_line.account_id:
                if retval['account_id']:
                    if retval['account_id'] != move_line.account_id.id:
                        retval['account_id'] = False
                        break
                else:
                    retval['account_id'] = move_line.account_id.id
            else:
                if retval['account_id']: 
                    retval['account_id'] = False
                    break
        for move_line in move_lines:
            if move_line.invoice:
                if retval['match_type']:
                    if retval['match_type'] != 'invoice':
                        retval['match_type'] = False
                        break
                else:
                    retval['match_type'] = 'invoice'
            else:
                if retval['match_type']: 
                    retval['match_type'] = False
                    break
        if move_lines and not retval['match_type']:
            retval['match_type'] = 'move'
        if move_lines and len(move_lines) == 1:
            retval['reference'] = move_lines[0].ref
        if retval['match_type'] == 'invoice':
            retval['invoice_ids'] = [x.invoice.id for x in move_lines]
            retval['type'] = type_map[move_lines[0].invoice.type]
        return retval
    
    def match(self, cr, uid, ids, results=None, context=None):
        if not ids:
            return True

        company_obj = self.pool.get('res.company')
        partner_bank_obj = self.pool.get('res.partner.bank')
        journal_obj = self.pool.get('account.journal')
        move_line_obj = self.pool.get('account.move.line')
        payment_line_obj = self.pool.get('payment.line')
        statement_line_obj = self.pool.get('account.bank.statement.line')
        payment_order_obj = self.pool.get('payment.order')

        # Results
        if results is None:
            results = dict(
                trans_loaded_cnt = 0,
                trans_skipped_cnt = 0,
                trans_matched_cnt = 0,
                bank_costs_invoice_cnt = 0,
                error_cnt = 0,
                log = [],
                )

        # Caching
        error_accounts = {}
        info = {}
        linked_payments = {}
        # TODO: harvest linked invoices from draft statement lines?
        linked_invoices = {}
        payment_lines = []

        # Get all unreconciled sent payment lines in one big swoop.
        # No filtering can be done, as empty dates carry value for C2B
        # communication. Most likely there are much less sent payments
        # than reconciled and open/draft payments.
        # Strangely, payment_orders still do not have company_id
        cr.execute("SELECT l.id FROM payment_order o, payment_line l "
                       "WHERE l.order_id = o.id AND "
                       "o.state = 'sent' AND "
                       "l.date_done IS NULL"
                       )
        payment_line_ids = [x[0] for x in cr.fetchall()]
        if payment_line_ids:
            payment_lines = payment_line_obj.browse(cr, uid, payment_line_ids)

        # Start the loop over the transactions requested to match
        transactions = self.browse(cr, uid, ids, context)
        # TODO: do we do injected transactions here?
        injected = []
        i = 0
        max_trans = len(transactions)
        while i < max_trans:
            move_info = False
            if injected:
                # Force FIFO behavior
                transaction = injected.pop(0)
            else:
                transaction = transactions[i]

            if (transaction.statement_line_id and
                transaction.statement_line_id.state == 'confirmed'):
                raise osv.except_osv(
                    _("Cannot perform match"),
                    _("Cannot perform match on a confirmed transction"))
            
            if transaction.local_account in error_accounts:
                results['trans_skipped_cnt'] += 1
                if not injected:
                    i += 1
                continue
            
            # TODO: optimize by ordering transactions per company, 
            # and perform the stanza below only once per company.
            # In that case, take newest transaction date into account
            # when retrieving move_line_ids below.
            company = company_obj.browse(
                cr, uid, transaction.company_id.id, context)
            # Get default defaults
            def_pay_account_id = company.partner_id.property_account_payable.id
            def_rec_account_id = company.partner_id.property_account_receivable.id

            # Get interesting journals once
            # Added type 'general' to capture fund transfers
            journal_ids = journal_obj.search(cr, uid, [
                    ('type', 'in', ('general', 'sale','purchase',
                                    'purchase_refund','sale_refund')),
                    ('company_id', '=', company.id),
                    ])
            # Get all unreconciled moves
            move_line_ids = move_line_obj.search(cr, uid, [
                    ('reconcile_id', '=', False),
                    ('journal_id', 'in', journal_ids),
                    ('account_id.reconcile', '=', True),
                    ('date', '<=', transaction.execution_date),
                    ])
            if move_line_ids:
                move_lines = move_line_obj.browse(cr, uid, move_line_ids)
            else:
                move_lines = []
            
            # Create fallback currency code
            currency_code = transaction.local_currency or company.currency_id.name

            # Check cache for account info/currency
            if transaction.local_account in info and \
               currency_code in info[transaction.local_account]:
                account_info = info[transaction.local_account][currency_code]
            else:
                # Pull account info/currency
                account_info = get_company_bank_account(
                    self.pool, cr, uid, transaction.local_account,
                    transaction.local_currency, company, results['log']
                )
                if not account_info:
                    results['log'].append(
                        _('Transaction found for unknown account %(bank_account)s') %
                        {'bank_account': transaction.local_account}
                    )
                    error_accounts[transaction.local_account] = True
                    results['error_cnt'] += 1
                    if not injected:
                        i += 1
                    continue
                if 'journal_id' not in account_info:
                    results['log'].append(
                        _('Transaction found for account %(bank_account)s, '
                          'but no default journal was defined.'
                         ) % {'bank_account': transaction.local_account}
                    )
                    error_accounts[transaction.local_account] = True
                    results['error_cnt'] += 1
                    if not injected:
                        i += 1
                    continue

                # Get required currency code
                currency_code = account_info.currency_id.name

                # Cache results
                if not transaction.local_account in info:
                    info[transaction.local_account] = {
                        currency_code: account_info
                    }
                else:
                    info[transaction.local_account][currency_code] = account_info

            # Final check: no coercion of currencies!
            if transaction.local_currency \
               and account_info.currency_id.name != transaction.local_currency:
                # TODO: convert currencies?
                results['log'].append(
                    _('transaction %(statement_id)s.%(transaction_id)s for account %(bank_account)s' 
                      ' uses different currency than the defined bank journal.'
                     ) % {
                         'bank_account': transactions.local_account,
                         'transaction_id': transaction.statement,
                         'statement_id': transaction.transaction,
                     }
                )
                error_accounts[transaction.local_account] = True
                results['error_cnt'] += 1
                if not injected:
                    i += 1
                continue

            # Link accounting period
            period_id = get_period(
                self.pool, cr, uid,
                str2date(transaction.effective_date,'%Y-%m-%d'), company,
                results['log'])
            if not period_id:
                results['trans_skipped_cnt'] += 1
                if not injected:
                    i += 1
                continue

            # When bank costs are part of transaction itself, split it.
            if transaction.type != bt.BANK_COSTS and transaction.provision_costs:
                # Create new transaction for bank costs
                cost_id = self.copy(
                    cr, uid, transaction.id,
                    dict(
                        type = bt.BANK_COSTS,
                        transaction = '%s-prov' % transaction.transaction,
                        transferred_amount = transaction.provision_costs,
                        remote_currency = transaction.provision_costs_currency,
                        message = transaction.provision_costs_description,
                        parent_id = transaction.id,
                        ), context)
                
                injected.append(self.browse(cr, uid, cost_id, context))
                
                # Remove bank costs from current transaction
                # Note that this requires that the transferred_amount
                # includes the bank costs and that the costs itself are
                # signed correctly.
                self.write(
                    cr, uid, transaction.id, 
                    dict(
                        transferred_amount =
                        transaction.transferred_amount - transaction.provision_costs,
                        provision_costs = False,
                        provision_costs_currency = False,
                        provision_costs_description = False,
                        ), context=context)
                # rebrowse the current record after writing
                transaction=self.browse(cr, uid, transaction.id, context=context)
            # Match full direct debit orders
            if transaction.type == bt.DIRECT_DEBIT:
                move_info = self._match_debit_order(
                    cr, uid, transaction, results['log'], context)
            if transaction.type == bt.STORNO:
                move_info = self._match_storno(
                    cr, uid, transaction, results['log'], context)
            # Allow inclusion of generated bank invoices
            if transaction.type == bt.BANK_COSTS:
                lines = self._match_costs(
                    cr, uid, transaction, period_id, account_info,
                    results['log']
                    )
                results['bank_costs_invoice_cnt'] += bool(lines)
                for line in lines:
                    if not [x for x in move_lines if x.id == line.id]:
                        move_lines.append(line)
                partner_ids = [account_info.bank_partner_id.id]
                partner_banks = []
            else:
                # Link remote partner, import account when needed
                partner_banks = get_bank_accounts(
                    self.pool, cr, uid, transaction.remote_account,
                    results['log'], fail=True
                    )
                if partner_banks:
                    partner_ids = [x.partner_id.id for x in partner_banks]
                elif transaction.remote_owner:
                    iban = sepa.IBAN(transaction.remote_account)
                    if iban.valid:
                        country_code = iban.countrycode
                    elif transaction.remote_owner_country_code:
                        country_code = transaction.remote_owner_country_code
                    # fallback on the import parsers country code
                    elif transaction.bank_country_code:
                        country_code = transaction.bank_country_code
                    elif company.partner_id and company.partner_id.country:
                        country_code = company.partner_id.country.code
                    else:
                        country_code = None
                    partner_id = get_or_create_partner(
                        self.pool, cr, uid, transaction.remote_owner,
                        transaction.remote_owner_address,
                        transaction.remote_owner_postalcode,
                        transaction.remote_owner_city,
                        country_code, results['log']
                        )
                    if transaction.remote_account:
                        partner_bank_id = create_bank_account(
                            self.pool, cr, uid, partner_id,
                            transaction.remote_account,
                            transaction.remote_owner, 
                            transaction.remote_owner_address,
                            transaction.remote_owner_city,
                            country_code, results['log']
                            )
                        partner_banks = partner_bank_obj.browse(
                            cr, uid, [partner_bank_id]
                            )
                    else:
                        partner_bank_id = None
                        partner_banks = []
                    partner_ids = [partner_id]
                else:
                    partner_ids = []
                    partner_banks = []

            # Credit means payment... isn't it?
            if (not move_info
                and transaction.transferred_amount < 0 and payment_lines):
                # Link open payment - if any
                move_info = self._match_payment(
                    cr, uid, transaction,
                    payment_lines, partner_ids,
                    partner_banks, results['log'], linked_payments,
                    )
                
            # Second guess, invoice -> may split transaction, so beware
            if not move_info:
                # Link invoice - if any. Although bank costs are not an
                # invoice, automatic invoicing on bank costs will create
                # these, and invoice matching still has to be done.
                
                transaction, move_info, remainder = self._match_invoice(
                    cr, uid, transaction, move_lines, partner_ids,
                    partner_banks, results['log'], linked_invoices,
                    context=context)
                if remainder:
                    injected.append(self.browse(cr, uid, remainder, context))

            account_id = move_info and move_info.get('account_id', False)
            if not account_id:
                # Use the default settings, but allow individual partner
                # settings to overrule this. Note that you need to change
                # the internal type of these accounts to either 'payable'
                # or 'receivable' to enable usage like this.
                if transaction.transferred_amount < 0:
                    if len(partner_banks) == 1:
                        account_id = (
                            partner_banks[0].partner_id.property_account_payable and
                            partner_banks[0].partner_id.property_account_payable.id)
                    if len(partner_banks) != 1 or not account_id or account_id == def_pay_account_id:
                        account_id = (account_info.default_credit_account_id and
                                      account_info.default_credit_account_id.id)
                else:
                    if len(partner_banks) == 1:
                        account_id = (
                            partner_banks[0].partner_id.property_account_receivable and
                            partner_banks[0].partner_id.property_account_receivable.id)
                    if len(partner_banks) != 1 or not account_id or account_id == def_rec_account_id:
                        account_id = (account_info.default_debit_account_id and
                                      account_info.default_debit_account_id.id)
            values = {}
            self_values = {}
            if move_info:
                results['trans_matched_cnt'] += 1
                self_values['match_type'] = move_info['match_type']
                self_values['payment_line_id'] = move_info.get('payment_line_id', False)
                self_values['move_line_ids'] = [(6, 0, move_info.get('move_line_ids') or [])]
                self_values['invoice_ids'] = [(6, 0, move_info.get('invoice_ids') or [])]
                self_values['payment_order_ids'] = [(6, 0, move_info.get('payment_order_ids') or [])]
                self_values['payment_order_id'] = (move_info.get('payment_order_ids', False) and 
                                                   len(move_info['payment_order_ids']) == 1 and
                                                   move_info['payment_order_ids'][0]
                                                   )
                self_values['move_line_id'] = (move_info.get('move_line_ids', False) and
                                               len(move_info['move_line_ids']) == 1 and
                                               move_info['move_line_ids'][0]
                                               )
                if move_info['match_type'] == 'invoice':
                    self_values['invoice_id'] = (move_info.get('invoice_ids', False) and
                                                 len(move_info['invoice_ids']) == 1 and
                                                 move_info['invoice_ids'][0]
                                                 )
                values['partner_id'] = move_info['partner_id']
                values['partner_bank_id'] = move_info['partner_bank_id']
                values['type'] = move_info['type']
                # values['match_type'] = move_info['match_type']
            else:
                values['partner_id'] = values['partner_bank_id'] = False
            if not values['partner_id'] and partner_ids and len(partner_ids) == 1:
                values['partner_id'] = partner_ids[0]
            if (not values['partner_bank_id'] and partner_banks and
                len(partner_banks) == 1):
                values['partner_bank_id'] = partner_banks[0].id
            if not transaction.statement_line_id:
                values.update(dict(
                        name = '%s.%s' % (transaction.statement, transaction.transaction),
                        date = transaction.effective_date,
                        amount = transaction.transferred_amount,
                        statement_id = transaction.statement_id.id,
                        note = transaction.message,
                        ref = transaction.reference,
                        period_id = period_id,
                        currency = account_info.currency_id.id,
                        account_id = account_id,
                        import_transaction_id = transaction.id,
                        ))
                statement_line_id = statement_line_obj.create(cr, uid, values, context)
                results['trans_loaded_cnt'] += 1
                self_values['statement_line_id'] = statement_line_id
            else:
                statement_line_obj.write(
                    cr, uid, transaction.statement_line_id.id, values, context)
            self.write(cr, uid, transaction.id, self_values, context)
            if not injected:
                i += 1

        if payment_lines:
            # As payments lines are treated as individual transactions, the
            # batch as a whole is only marked as 'done' when all payment lines
            # have been reconciled.
            cr.execute(
                "SELECT DISTINCT o.id "
                "FROM payment_order o, payment_line l "
                "WHERE o.state = 'sent' "
                  "AND o.id = l.order_id "
                  "AND o.id NOT IN ("
                    "SELECT DISTINCT order_id AS id "
                    "FROM payment_line "
                    "WHERE date_done IS NULL "
                      "AND id IN (%s)"
                   ")" % (','.join([str(x) for x in payment_line_ids]))
            )
            order_ids = [x[0] for x in cr.fetchall()]
            if order_ids:
                # Use workflow logics for the orders. Recode logic from
                # account_payment, in order to increase efficiency.
                payment_order_obj.set_done(cr, uid, order_ids,
                                        {'state': 'done'}
                                       )
                wf_service = netsvc.LocalService('workflow')
                for id in order_ids:
                    wf_service.trg_validate(
                        uid, 'payment.order', id, 'done', cr)

    def _get_residual(self, cr, uid, ids, name, args, context=None):
        """
        Calculate the residual against the candidate reconciliation.
        When 
              
              55 debiteuren, 50 binnen: amount > 0, residual > 0
              -55 crediteuren, -50 binnen: amount = -60 residual -55 - -50
              
              - residual > 0 and transferred amount > 0, or
              - residual < 0 and transferred amount < 0

        the result is a partial reconciliation. In the other cases,
        a new statement line can be split off.

        We should give users the option to reconcile with writeoff
        or partial reconciliation / new statement line
        """

        if not ids:
            return {}
        res = dict([(x, False) for x in ids])
        move_line_obj = self.pool.get('account.move.line')
        for transaction in self.browse(cr, uid, ids, context):
            if (transaction.statement_line_id.state == 'draft'
                and transaction.match_type in 
                [('invoice'), ('move'), ('manual')]
                and transaction.move_line_id):
                rec_moves = (
                    transaction.move_line_id.reconcile_id and 
                    transaction.move_line_id.reconcile_id.line_id or
                    transaction.move_line_id.reconcile_partial_id and
                    transaction.move_line_id.reconcile_partial_id.line_partial_ids or
                    [transaction.move_line_id])
                res[transaction.id] = (
                    move_line_obj.get_balance(cr, uid, [x.id for x in rec_moves])
                    - transaction.transferred_amount)
        return res
        
    def _get_match_multi(self, cr, uid, ids, name, args, context=None):
        """
        Indicate in the wizard that multiple matches have been found
        and that the user has not yet made a choice between them.
        """
        if not ids:
            return {}
        res = dict([(x, False) for x in ids])
        for transaction in self.browse(cr, uid, ids, context):
            if transaction.match_type == 'move':
                if transaction.move_line_ids and not transaction.move_line_id:
                    res[transaction.id] = True
            elif transaction.match_type == 'invoice':
                if transaction.invoice_ids and not transaction.invoice_id:
                    res[transaction.id] = True
            elif transaction.match_type == 'payment_order':
                if (transaction.payment_order_ids and not
                    transaction.payment_order_id):
                    res[transaction.id] = True
        return res
    
    def clear_and_write(self, cr, uid, ids, vals=None, context=None):
        """
        Write values in argument 'vals', but clear all match
        related values first
        """
        write_vals = (dict([(x, False) for x in [
                    'match_type',
                    'move_line_id', 
                    'invoice_id', 
                    'manual_invoice_id', 
                    'manual_move_line_id',
                    'payment_line_id',
                    ]] +
                     [(x, [(6, 0, [])]) for x in [
                        'move_line_ids',
                        'invoice_ids',
                        'payment_order_ids',
                        ]]))
        write_vals.update(vals or {})
        return self.write(cr, uid, ids, write_vals, context=context)

    column_map = {
        # used in bank_import.py, converting non-osv transactions
        'statement_id': 'statement',
        'id': 'transaction'
        }
                
    _columns = {
        # start mem_bank_transaction atributes
        # see parsers/models.py
        'transaction': fields.char('transaction', size=16), # id
        'statement': fields.char('statement', size=16), # statement_id
        'type': fields.char('type', size=16),
        'reference': fields.char('reference', size=1024),
        'local_account': fields.char('local_account', size=24),
        'local_currency': fields.char('local_currency', size=16),
        'execution_date': fields.date('execution_date'),
        'effective_date': fields.date('effective_date'),
        'remote_account': fields.char('remote_account', size=24),
        'remote_currency': fields.char('remote_currency', size=16),
        'exchange_rate': fields.float('exchange_rate'),
        'transferred_amount': fields.float('transferred_amount'),
        'message': fields.char('message', size=1024),
        'remote_owner': fields.char('remote_owner', size=24),
        'remote_owner_address': fields.char('remote_owner_address', size=24),
        'remote_owner_city': fields.char('remote_owner_city', size=24),
        'remote_owner_postalcode': fields.char('remote_owner_postalcode', size=24),
        'remote_owner_country_code': fields.char('remote_owner_country_code', size=24),
        'remote_owner_custno': fields.char('remote_owner_custno', size=24),
        'remote_bank_bic': fields.char('remote_bank_bic', size=24),
        'remote_bank_bei': fields.char('remote_bank_bei', size=24),
        'remote_bank_ibei': fields.char('remote_bank_ibei', size=24),
        'remote_bank_eangl': fields.char('remote_bank_eangln', size=24),
        'remote_bank_chips_uid': fields.char('remote_bank_chips_uid', size=24),
        'remote_bank_duns': fields.char('remote_bank_duns', size=24),
        'remote_bank_tax_id': fields.char('remote_bank_tax_id', size=24),
        'provision_costs': fields.float('provision_costs', size=24),
        'provision_costs_currency': fields.char('provision_costs_currency', size=64),
        'provision_costs_description': fields.char('provision_costs_description', size=24),
        'error_message': fields.char('error_message', size=1024),
        'storno_retry': fields.boolean('storno_retry'),
        # end of mem_bank_transaction_fields
        'bank_country_code': fields.char(
            'Bank country code', size=2,
            help=("Fallback default country for new partner records, "
                  "as defined by the import parser"),
            readonly=True,),
        'company_id': fields.many2one(
            'res.company', 'Company', required=True),
        'duplicate': fields.boolean('duplicate'),
        'statement_line_id': fields.many2one(
            'account.bank.statement.line', 'Statement line',
            ondelete='CASCADE'),
        'statement_id': fields.many2one(
            'account.bank.statement', 'Statement'),
        'parent_id': fields.many2one(
            'banking.import.transaction', 'Split off from this transaction'),
        # match fields
        'match_type': fields.selection(
            [('manual', 'Manual'), ('move','Move'), ('invoice', 'Invoice'),
             ('payment', 'Payment'), ('payment_order', 'Payment order'),
             ('storno', 'Storno')],
            'Match type'),
        'match_multi': fields.function(
            _get_match_multi, method=True, string='Multi match',
            type='boolean'),
        'payment_order_ids': fields.many2many(
            'payment.order', 'banking_transaction_payment_order_rel',
            'order_id', 'transaction_id', 'Payment orders'),
        'payment_order_id': fields.many2one(
            'payment.order', 'Payment order to reconcile'),
        'move_line_ids': fields.many2many(
            'account.move.line', 'banking_transaction_move_line_rel',
            'move_line_id', 'transaction_id', 'Matching entries'),
        'move_line_id': fields.many2one(
            'account.move.line', 'Entry to reconcile'),
        'payment_line_id': fields.many2one('payment.line', 'Payment line'),
        'invoice_ids': fields.many2many(
            'account.invoice', 'banking_transaction_invoice_rel',
            'invoice_id', 'transaction_id', 'Matching invoices'),
        'invoice_id': fields.many2one(
            'account.invoice', 'Invoice to reconcile'),
        'payment_line_id': fields.many2one('payment.line', 'Payment line'),
        'residual': fields.function(
            _get_residual, method=True, string='Residual', type='float'),
        'writeoff_account_id': fields.many2one(
            'account.account', 'Write-off account',
             domain=[('type', '!=', 'view')]),
        'writeoff_journal_id': fields.many2one(
            'account.journal', 'Write-off journal'),
        'writeoff_move_line_id': fields.many2one(
            'account.move.line', 'Write off move line'),
        }
    _defaults = {
        'company_id': lambda s,cr,uid,c:
            s.pool.get('res.company')._company_default_get(
            cr, uid, 'bank.import.transaction', context=c),
        }
banking_import_transaction()

class account_bank_statement_line(osv.osv):
    _inherit = 'account.bank.statement.line'
    _columns = {
        'import_transaction_id': fields.many2one(
            'banking.import.transaction', 
            'Import transaction', readonly=True),
        'match_multi': fields.related(
            'import_transaction_id', 'match_multi', type='boolean',
            string='Multi match', readonly=True),
        'residual': fields.related(
            'import_transaction_id', 'residual', type='float', 
            string='Residual'),
        'duplicate': fields.related(
            'import_transaction_id', 'duplicate', type='boolean',
            string='Possible duplicate import', readonly=True),
        'match_type': fields.related(
            'import_transaction_id', 'match_type', type='selection',
            selection=[('manual', 'Manual'), ('move','Move'),
                       ('invoice', 'Invoice'), ('payment', 'Payment'),
                       ('payment_order', 'Payment order'),
                       ('storno', 'Storno')], 
            string='Match type', readonly=True,),
        'residual': fields.related(
            'import_transaction_id', 'residual', type='float',
            string='Residual', readonly=True,
            ),
        'state': fields.selection(
            [('draft', 'Draft'), ('confirmed', 'Confirmed')], 'State',
            readonly=True, required=True),
        'move_id': fields.many2one(
            'account.move', 'Move', readonly=True,
            help="The accounting move associated with this line"),
        }

    _defaults = {
        'state': 'draft',
        }

    def match_wizard(self, cr, uid, ids, context=None):
        res = False
        if ids:
            if isinstance(ids, (int, float)):
                ids = [ids]
            if context is None:
                context = {}
            context['statement_line_id'] = ids[0]
            wizard_obj = self.pool.get('banking.transaction.wizard')
            res_id = wizard_obj.create(
                cr, uid, {'statement_line_id': ids[0]}, context=context)
            res = wizard_obj.create_act_window(cr, uid, res_id, context=context)
        return res
        
    def confirm(self, cr, uid, ids, context=None):
        # TODO: a confirmed transaction should remove its reconciliation target
        # from other transactions where it is one of multiple candidates or
        # even the proposed reconciliation target.
        statement_obj = self.pool.get('account.bank.statement')
        obj_seq = self.pool.get('ir.sequence')
        import_transaction_obj = self.pool.get('banking.import.transaction')

        for st_line in self.browse(cr, uid, ids, context):
            if st_line.state != 'draft':
                continue
            if st_line.duplicate:
                raise osv.except_osv(
                    _('Bank transfer flagged as duplicate'),
                    _("You cannot confirm a bank transfer marked as a "
                      "duplicate (%s.%s)") % 
                    (st_line.statement_id.name, st_line.name,))
            if st_line.analytic_account_id:
                if not st_line.statement_id.journal_id.analytic_journal_id:
                    raise osv.except_osv(
                        _('No Analytic Journal !'),
                        _("You have to define an analytic journal on the '%s' "
                          "journal!") % (st_line.statement_id.journal_id.name,))
            if not st_line.amount:
                continue
            if st_line.import_transaction_id:
                import_transaction_obj.reconcile(
                    cr, uid, st_line.import_transaction_id.id, context)
                
            if not st_line.statement_id.name == '/':
                st_number = st_line.statement_id.name
            else:
                if st_line.statement_id.journal_id.sequence_id:
                    c = {'fiscalyear_id': 
                         st_line.statement_id.period_id.fiscalyear_id.id}
                    st_number = obj_seq.get_id(
                        cr, uid, 
                        st_line.statement_id.journal_id.sequence_id.id, 
                        context=c)
                else:
                    st_number = obj_seq.get(cr, uid, 'account.bank.statement')
                statement_obj.write(
                    cr, uid, [st_line.statement_id.id], 
                    {'name': st_number}, context=context)

            st_line_number = statement_obj.get_next_st_line_number(
                cr, uid, st_number, st_line, context)
            company_currency_id = st_line.statement_id.journal_id.company_id.currency_id.id
            move_id = statement_obj.create_move_from_st_line(
                cr, uid, st_line.id, company_currency_id, 
                st_line_number, context)
            self.write(
                cr, uid, st_line.id, 
                {'state': 'confirmed', 'move_id': move_id}, context)
        return True

    def cancel(self, cr, uid, ids, context=None):
        if ids and isinstance(ids, (int, float)):
            ids = [ids]
        account_move_obj = self.pool.get('account.move')
        import_transaction_obj = self.pool.get('banking.import.transaction')
        transaction_cancel_ids = []
        move_unlink_ids = []
        set_draft_ids = []
        # harvest ids for various actions
        for st_line in self.browse(cr, uid, ids, context):
            if st_line.state != 'confirmed':
                continue
            if st_line.statement_id.state != 'draft':
                raise osv.except_osv(
                    _("Cannot cancel bank transaction"),
                    _("The bank statement that this transaction belongs to has "
                      "already been confirmed"))
            if st_line.import_transaction_id:
                transaction_cancel_ids.append(st_line.import_transaction_id.id)
            if st_line.move_id:
                move_unlink_ids.append(st_line.move_id.id)
            else:
                raise osv.except_osv(
                    _("Cannot cancel bank transaction"),
                    _("Cannot cancel this bank transaction. The information "
                      "needed to undo the accounting entries has not been "
                      "recorded"))
            set_draft_ids.append(st_line.id)
        # perform actions
        import_transaction_obj.cancel(
            cr, uid, transaction_cancel_ids, context=context)
        account_move_obj.button_cancel(cr, uid, move_unlink_ids, context)
        account_move_obj.unlink(cr, uid, move_unlink_ids, context)
        self.write(
            cr, uid, set_draft_ids, {'state': 'draft'}, context=context)
        return True
account_bank_statement_line()

class account_bank_statement(osv.osv):
    _inherit = 'account.bank.statement'

    def _end_balance(self, cursor, user, ids, name, attr, context=None):
        """
        This method taken from account/account_bank_statement.py and
        altered to take the statement line subflow into account
        """

        res_currency_obj = self.pool.get('res.currency')
        res_users_obj = self.pool.get('res.users')
        res = {}

        company_currency_id = res_users_obj.browse(cursor, user, user,
                context=context).company_id.currency_id.id

        statements = self.browse(cursor, user, ids, context=context)
        for statement in statements:
            res[statement.id] = statement.balance_start
            currency_id = statement.currency.id
            for line in statement.move_line_ids:
                if line.debit > 0:
                    if line.account_id.id == \
                            statement.journal_id.default_debit_account_id.id:
                        res[statement.id] += res_currency_obj.compute(cursor,
                                user, company_currency_id, currency_id,
                                line.debit, context=context)
                else:
                    if line.account_id.id == \
                            statement.journal_id.default_credit_account_id.id:
                        res[statement.id] -= res_currency_obj.compute(cursor,
                                user, company_currency_id, currency_id,
                                line.credit, context=context)
            if statement.state == 'draft':
                for line in statement.line_ids:
                    ### start modifications banking-addons ###
                    # res[statement.id] += line.amount
                    if line.state == 'draft':
                        res[statement.id] += line.amount
                    ### end modifications banking-addons ###

        for r in res:
            res[r] = round(res[r], 2)
        return res

    def button_confirm_bank(self, cr, uid, ids, context=None):
        """ Inject the statement line workflow here """
        if context is None:
            context = {}
        line_obj = self.pool.get('account.bank.statement.line')
        for st in self.browse(cr, uid, ids, context=context):
            j_type = st.journal_id.type
            if not self.check_status_condition(cr, uid, st.state, journal_type=j_type):
                continue

            self.balance_check(cr, uid, st.id, journal_type=j_type, context=context)
            if (not st.journal_id.default_credit_account_id) \
                    or (not st.journal_id.default_debit_account_id):
                raise osv.except_osv(_('Configuration Error !'),
                        _('Please verify that an account is defined in the journal.'))

            # protect against misguided manual changes
            for line in st.move_line_ids:
                if line.state <> 'valid':
                    raise osv.except_osv(_('Error !'),
                            _('The account entries lines are not in valid state.'))

            line_obj.confirm(cr, uid, [line.id for line in st.line_ids], context)
            self.log(cr, uid, st.id, _('Statement %s is confirmed, journal '
                                       'items are created.') % (st.name,))
        return self.write(cr, uid, ids, {'state':'confirm'}, context=context)

    def button_cancel(self, cr, uid, ids, context=None):
        """ 
        Do nothing but write the state. Delegate all actions to the statement
        line workflow instead.
        """
        self.write(cr, uid, ids, {'state':'draft'}, context=context)

    _columns = {
        # override this field *only* to replace the 
        # function method with the one from this module.
        # Note that it is defined twice, both in
        # account/account_bank_statement.py (without 'store') and
        # account/account_cash_statement.py (with store=True)
        
        'balance_end': fields.function(
            _end_balance, method=True, store=True, string='Balance'),
        }

account_bank_statement()
