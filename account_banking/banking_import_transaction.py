# coding: utf-8
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#              (C) 2011 Therp BV (<http://therp.nl>).
#              (C) 2011 Smile (<http://smile.fr>).
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

import datetime
from openerp.osv import orm, fields
from openerp import netsvc
from openerp.tools.translate import _
from openerp.addons.decimal_precision import decimal_precision as dp
from .parsers import models
from .parsers import convert
from .wizard import banktools

bt = models.mem_bank_transaction


class banking_import_transaction(orm.Model):
    """ orm representation of mem_bank_transaction() for interactive and posthoc
    configuration of reconciliation in the bank statement view.

    Possible refractoring in OpenERP 6.1:
    merge with bank_statement_line, using sparse fields

    """
    _name = 'banking.import.transaction'
    _description = 'Bank import transaction'
    _rec_name = 'transaction'

    # This variable is used to match supplier invoices with an invoice date
    # after the real payment date. This can occur with online transactions
    # (web shops).
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
        amount = round(abs(trans.statement_line_id.amount), digits)
        # Make sure to be able to pinpoint our costs invoice for later
        # matching
        reference = '%s.%s: %s' % (trans.statement,
                                   trans.transaction,
                                   trans.reference)

        # search supplier invoice
        invoice_obj = self.pool.get('account.invoice')
        invoice_ids = invoice_obj.search(
            cr, uid,
            [
                '&',
                ('type', '=', 'in_invoice'),
                ('partner_id', 'child_of', account_info.bank_partner_id.id),
                ('company_id', '=', account_info.company_id.id),
                ('date_invoice', '=', trans.execution_date),
                ('reference', '=', reference),
                ('amount_total', '=', amount),
            ]
        )
        if invoice_ids and len(invoice_ids) == 1:
            invoice = invoice_obj.browse(cr, uid, invoice_ids)[0]
        elif not invoice_ids:
            # create supplier invoice
            partner_obj = self.pool.get('res.partner')
            invoice_lines = [(0, 0, dict(
                amount=1,
                price_unit=amount,
                name=trans.message or trans.reference,
                account_id=account_info.costs_account_id.id
            ))]
            invoice_address_id = partner_obj.address_get(
                cr, uid, [account_info.bank_partner_id.id], ['invoice']
            )
            invoice_id = invoice_obj.create(cr, uid, dict(
                type='in_invoice',
                company_id=account_info.company_id.id,
                partner_id=account_info.bank_partner_id.id,
                address_invoice_id=invoice_address_id['invoice'],
                period_id=period_id,
                journal_id=account_info.invoice_journal_id.id,
                account_id=(
                    account_info.bank_partner_id.property_account_payable.id),
                date_invoice=trans.execution_date,
                reference_type='none',
                reference=reference,
                name=trans.reference or trans.message,
                check_total=amount,
                invoice_line=invoice_lines,
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

    def _match_invoice(self, cr, uid, trans, move_lines,
                       partner_ids, bank_account_ids,
                       log, linked_invoices,
                       context=None):
        '''
        Find the invoice belonging to this reference - if there is one
        Use the sales journal to check.

        Challenges we're facing:
            1. The sending or receiving party is not necessarily the same as
               the partner the payment relates to.
            2. References can be messed up during manual encoding and inexact
               matching can link the wrong invoices.
            3. Amounts can or can not match the expected amount.
            4. Multiple invoices can be paid in one transaction.
            .. There are countless more, but these we'll try to address.

        Assumptions for matching:
            1. There are no payments for invoices not sent. These are dealt
               with later on.
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
               Statements are encoded in draft. You will have the opportunity
               to manually correct the wrong assumptions.

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
            if invoice.type.startswith('in_'):
                return invoice.name or invoice.number
            else:
                return invoice.number

        def has_id_match(invoice, ref, msg):
            '''
            Aid for debugging - way more comprehensible than complex
            comprehension filters ;-)

            Match on ID of invoice (reference, name or number, whatever
            available and sensible)
            '''
            if invoice.reference and len(invoice.reference) > 2:
                # Reference always comes first, as it is manually set for a
                # reason.
                iref = invoice.reference.upper()
                if iref in ref or iref in msg:
                    return True
            if invoice.origin and len(invoice.origin) > 2:
                iorigin = invoice.origin.upper()
                if iorigin in ref or iorigin in msg:
                    return True
            if invoice.type.startswith('in_'):
                # Internal numbering, no likely match on number
                if invoice.name and len(invoice.name) > 2:
                    iname = invoice.name.upper()
                    if iname in ref or iname in msg:
                        return True
                if (invoice.supplier_invoice_number and
                        len(invoice.supplier_invoice_number) > 2):
                    supp_ref = invoice.supplier_invoice_number.upper()
                    if supp_ref in ref or supp_ref in msg:
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

            # '''Check if the move_line has been cached'''
            # return move_line.id in linked_invoices

        def _cache(move_line, remaining=0.0):
            '''Cache the move_line'''
            linked_invoices[move_line.id] = remaining

        def _remaining(move_line):
            '''Return the remaining amount for a previously matched move_line
            '''
            return linked_invoices[move_line.id]

        def _sign(invoice):
            '''Return the direction of an invoice'''
            return {
                'in_invoice': -1,
                'in_refund': 1,
                'out_invoice': 1,
                'out_refund': -1
            }[invoice.type]

        def is_zero(move_line, total):
            return self.pool.get('res.currency').is_zero(
                cr, uid, trans.statement_id.currency, total)

        digits = dp.get_precision('Account')(cr)[1]
        partial = False

        # Search invoice on partner
        if partner_ids:
            candidates = [
                x for x in move_lines
                if x.partner_id.id in partner_ids and
                (convert.str2date(x.date, '%Y-%m-%d') <=
                 (convert.str2date(trans.execution_date, '%Y-%m-%d') +
                  self.payment_window)) and
                (not _cached(x) or _remaining(x))
            ]
        else:
            candidates = []

        # Next on reference/invoice number. Mind that this uses the invoice
        # itself, as the move_line references have been fiddled with on invoice
        # creation. This also enables us to search for the invoice number in
        # the reference instead of the other way around, as most human
        # interventions *add* text.
        ref = trans.reference.upper()
        msg = trans.message.upper()
        if len(candidates) > 1 or not candidates:
            # The manual usage of the sales journal creates moves that
            # are not tied to invoices. Thanks to Stefan Rijnhart for
            # reporting this.
            candidates = [
                x for x in candidates or move_lines
                if (x.invoice and has_id_match(x.invoice, ref, msg) and
                    convert.str2date(x.invoice.date_invoice, '%Y-%m-%d') <=
                    (convert.str2date(trans.execution_date, '%Y-%m-%d') +
                     self.payment_window) and
                    (not _cached(x) or _remaining(x)) and
                    (not partner_ids or
                     x.invoice.partner_id.id in partner_ids))
            ]

        # Match on amount expected. Limit this kind of search to known
        # partners.
        if not candidates and partner_ids:
            candidates = [
                x for x in move_lines
                if (is_zero(x.move_id, ((x.debit or 0.0) - (x.credit or 0.0)) -
                            trans.statement_line_id.amount) and
                    convert.str2date(x.date, '%Y-%m-%d') <=
                    (convert.str2date(trans.execution_date, '%Y-%m-%d') +
                    self.payment_window) and
                    (not _cached(x) or _remaining(x)) and
                    x.partner_id.id in partner_ids)
            ]

        move_line = False

        if candidates and len(candidates) > 0:
            # Now a possible selection of invoices has been found, check the
            # amounts expected and received.
            #
            # TODO: currency coercing
            best = [
                x for x in candidates
                if (is_zero(x.move_id, ((x.debit or 0.0) - (x.credit or 0.0)) -
                            trans.statement_line_id.amount) and
                    convert.str2date(x.date, '%Y-%m-%d') <=
                    (convert.str2date(trans.execution_date, '%Y-%m-%d') +
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
                paid = [
                    x for x in move_lines
                    if x.invoice and has_id_match(x.invoice, ref, msg) and
                    convert.str2date(x.invoice.date_invoice, '%Y-%m-%d') <=
                    convert.str2date(trans.execution_date, '%Y-%m-%d') and
                    (_cached(x) and not _remaining(x))
                ]
                if paid:
                    log.append(
                        _('Unable to link transaction id %(trans)s '
                          '(ref: %(ref)s) to invoice: '
                          'invoice %(invoice)s was already paid') % {
                              'trans': '%s.%s' % (trans.statement,
                                                  trans.transaction),
                              'ref': trans.reference,
                              'invoice': eyecatcher(paid[0].invoice)})
                else:
                    # Multiple matches
                    # TODO select best bank account in this case
                    return (trans, self._get_move_info(
                            cr, uid, [x.id for x in candidates]),
                            False)
                move_line = False
                partial = False

            elif len(candidates) == 1 and candidates[0].invoice:
                # Mismatch in amounts
                move_line = candidates[0]
                invoice = move_line.invoice
                expected = round(_sign(invoice) * invoice.residual, digits)
                partial = True

            trans2 = None
            if move_line and partial:
                found = round(trans.statement_line_id.amount, digits)
                if abs(expected) == abs(found):
                    partial = False
                    # Last partial payment will not flag invoice paid without
                    # manual assistence
                    # Stefan: disabled this here for the interactive method
                    # Handled this with proper handling of partial
                    # reconciliation and the workflow service
                    # invoice_obj = self.pool.get('account.invoice')
                    # invoice_obj.write(cr, uid, [invoice.id], {
                    #     'state': 'paid'
                    #  })
                elif abs(expected) > abs(found):
                    # Partial payment, reuse invoice
                    _cache(move_line, expected - found)
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

    def _confirm_move(self, cr, uid, transaction_id, context=None):
        """
        The line is matched against a move (invoice), so generate a payment
        voucher with the write-off settings that the user requested. The move
        lines will be generated by the voucher, handling rounding and currency
        conversion.
        """
        if context is None:
            context = {}

        statement_line_pool = self.pool.get('account.bank.statement.line')
        transaction = self.browse(cr, uid, transaction_id, context)
        if not transaction.move_line_id:
            if transaction.match_type == 'invoice':
                raise orm.except_orm(
                    _("Cannot link transaction %s with invoice") %
                    transaction.statement_line_id.name,
                    (transaction.invoice_ids and
                     (_("Please select one of the matches in transaction "
                        "%s.%s") or
                      _("No match found for transaction %s.%s")) % (
                          transaction.statement_line_id.statement_id.name,
                          transaction.statement_line_id.name
                     )))
            else:
                raise orm.except_orm(
                    _("Cannot link transaction %s with accounting entry") %
                    transaction.statement_line_id.name,
                    (transaction.move_line_ids and
                     (_("Please select one of the matches in transaction "
                        "%s.%s") or
                      _("No match found for transaction %s.%s")) % (
                          transaction.statement_line_id.statement_id.name,
                          transaction.statement_line_id.name
                     )))

        st_line = transaction.statement_line_id
        journal = st_line.statement_id.journal_id
        if st_line.amount < 0.0:
            voucher_type = 'payment'
            account_id = (journal.default_debit_account_id and
                          journal.default_debit_account_id.id or False)
        else:
            voucher_type = 'receipt'
            account_id = (journal.default_credit_account_id and
                          journal.default_credit_account_id.id or False)

        # Use the statement line's date determine the period
        ctxt = context.copy()
        ctxt['company_id'] = st_line.company_id.id
        if 'period_id' in ctxt:
            del ctxt['period_id']
        period_id = self.pool.get('account.period').find(
            cr, uid, st_line.date, context=ctxt)[0]

        # Convert the move line amount to the journal currency
        move_line_amount = transaction.move_line_id.amount_residual_currency
        to_curr_id = (st_line.statement_id.journal_id.currency and
                      st_line.statement_id.journal_id.currency.id or
                      st_line.statement_id.company_id.currency_id.id)
        from_curr_id = (transaction.move_line_id.currency_id and
                        transaction.move_line_id.currency_id.id or
                        st_line.statement_id.company_id.currency_id.id)
        if from_curr_id != to_curr_id:
            amount_currency = statement_line_pool._convert_currency(
                cr, uid, from_curr_id, to_curr_id, move_line_amount,
                round=True, date=transaction.move_line_id.date,
                context=context)
        else:
            amount_currency = move_line_amount

        # Check whether this is a full or partial reconciliation
        if transaction.payment_option == 'with_writeoff':
            writeoff = abs(st_line.amount) - abs(amount_currency)
            line_amount = abs(amount_currency)
        else:
            writeoff = 0.0
            line_amount = abs(st_line.amount)

        # Define the voucher
        voucher = {
            'journal_id': st_line.statement_id.journal_id.id,
            'partner_id': (
                st_line.partner_id and st_line.partner_id.id or False),
            'company_id': st_line.company_id.id,
            'type': voucher_type,
            'account_id': account_id,
            'amount': abs(st_line.amount),
            'writeoff_amount': writeoff,
            'payment_option': transaction.payment_option,
            'writeoff_acc_id': transaction.writeoff_account_id.id,
            'analytic_id': transaction.writeoff_analytic_id.id or False,
            'date': st_line.date,
            'date_due': st_line.date,
            'period_id': period_id,
            'payment_rate_currency_id': to_curr_id,
        }

        # Define the voucher line
        vch_line = {
            # 'voucher_id': v_id,
            'move_line_id': transaction.move_line_id.id,
            'reconcile': True,
            'amount': line_amount,
            'account_id': transaction.move_line_id.account_id.id,
            'type': transaction.move_line_id.credit and 'dr' or 'cr',
        }
        voucher['line_ids'] = [(0, 0, vch_line)]
        # Voucher insists of taking journal from the context
        voucher_ctxt = dict(
            context, journal_id=st_line.statement_id.journal_id.id)
        voucher_id = self.pool.get('account.voucher').create(
            cr, uid, voucher, context=voucher_ctxt)
        statement_line_pool.write(
            cr, uid, st_line.id,
            {'voucher_id': voucher_id}, context=context)
        transaction.refresh()

    def _legacy_do_move_unreconcile(self, cr, uid, move_line_ids, currency,
                                    context=None):
        """
        Legacy method. Allow for canceling bank statement lines that
        were confirmed using earlier versions of the interactive wizard branch.

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
        move_lines = move_line_obj.browse(cr, uid, move_line_ids,
                                          context=context)
        reconcile = (move_lines[0].reconcile_id or
                     move_lines[0].reconcile_partial_id)
        line_ids = [
            x.id
            for x in reconcile.line_id or reconcile.line_partial_ids
        ]
        for move_line_id in move_line_ids:
            line_ids.remove(move_line_id)
        if len(line_ids) > 1:
            full = self.pool['res.currency'].is_zero(
                cr, uid, currency,
                move_line_obj.get_balance(cr, uid, line_ids))
            if full:
                line_partial_ids = []
            else:
                line_partial_ids = list(line_ids)
                line_ids = []
            reconcile_obj.write(
                cr, uid, reconcile.id,
                {'line_partial_ids': [(6, 0, line_partial_ids)],
                 'line_id': [(6, 0, line_ids)],
                 }, context=context)
        else:
            reconcile_obj.unlink(cr, uid, reconcile.id, context=context)
        for move_line in move_lines:
            if move_line.invoice:
                # reopening the invoice
                netsvc.LocalService('workflow').trg_validate(
                    uid, 'account.invoice', move_line.invoice.id, 'undo_paid',
                    cr
                )
        return True

    def _legacy_clear_up_writeoff(self, cr, uid, transaction, context=None):
        """
        Legacy method to support upgrades older installations of the
        interactive wizard branch. To be removed after 7.0
        clear up the writeoff move
        """
        if transaction.writeoff_move_line_id:
            move_pool = self.pool.get('account.move')
            move_pool.button_cancel(
                cr, uid, [transaction.writeoff_move_line_id.move_id.id],
                context=context)
            move_pool.unlink(
                cr, uid, [transaction.writeoff_move_line_id.move_id.id],
                context=context)
        return True

    def _legacy_cancel_move(self, cr, uid, transaction, context=None):
        """
        Legacy method to support upgrades from older installations
        of the interactive wizard branch.

        Undo the reconciliation of a transaction with a move line
        in the system: Retrieve the move line from the bank statement line's
        move that is reconciled with the matching move line recorded
        on the transaction. Do not actually remove the latter from the
        reconciliation, as it may be further reconciled.
        Unreconcile the bank statement move line and the optional
        write-off move line
        """
        statement_line_obj = self.pool.get('account.bank.statement.line')
        currency = transaction.statement_line_id.statement_id.currency
        reconcile_id = (
            transaction.move_line_id.reconcile_id and
            transaction.move_line_id.reconcile_id.id or
            transaction.move_line_id.reconcile_partial_id and
            transaction.move_line_id.reconcile_partial_id.id
        )
        move_lines = []
        for move in transaction.statement_line_id.move_ids:
            move_lines += move.line_id
        for line in move_lines:
            line_reconcile = line.reconcile_id or line.reconcile_partial_id
            if line_reconcile and line_reconcile.id == reconcile_id:
                st_line_line = line
                break
        line_ids = [st_line_line.id]
        # Add the write off line
        if transaction.writeoff_move_line_id:
            line_ids.append(transaction.writeoff_move_line_id.id)
        self._legacy_do_move_unreconcile(
            cr, uid, line_ids, currency, context=context)
        statement_line_obj.write(
            cr, uid, transaction.statement_line_id.id,
            {'reconcile_id': False}, context=context)

    def _cancel_voucher(self, cr, uid, transaction_id, context=None):
        voucher_pool = self.pool.get('account.voucher')
        transaction = self.browse(cr, uid, transaction_id, context=context)
        st_line = transaction.statement_line_id
        if transaction.match_type:
            if st_line.voucher_id:
                # Although vouchers can be associated with statement lines
                # in standard OpenERP, we consider ourselves owner of the
                # voucher if the line has an associated transaction
                # Upon canceling of the statement line/transaction,
                # we cancel and delete the vouchers.
                # Otherwise, the statement line will leave the voucher
                # unless the statement line itself is deleted.
                voucher_pool.cancel_voucher(
                    cr, uid, [st_line.voucher_id.id], context=context)
                voucher_pool.action_cancel_draft(
                    cr, uid, [st_line.voucher_id.id], context=context)
                voucher_pool.unlink(
                    cr, uid, [st_line.voucher_id.id], context=context)
                if (transaction.move_line_id and
                        transaction.move_line_id.invoice):
                    # reopening the invoice
                    netsvc.LocalService('workflow').trg_validate(
                        uid, 'account.invoice',
                        transaction.move_line_id.invoice.id, 'undo_paid', cr)
            # Allow canceling of legacy entries
            if not st_line.voucher_id and st_line.reconcile_id:
                self._legacy_cancel_move(cr, uid, transaction, context=context)

        return True

    cancel_map = {
        'invoice': _cancel_voucher,
        'manual': _cancel_voucher,
        'move': _cancel_voucher,
    }

    def cancel(self, cr, uid, ids, context=None):
        if ids and isinstance(ids, (int, float)):
            ids = [ids]
        for transaction in self.browse(cr, uid, ids, context):
            if not transaction.match_type:
                continue
            if transaction.match_type not in self.cancel_map:
                raise orm.except_orm(
                    _("Cannot cancel type %s" % transaction.match_type),
                    _("No method found to cancel this type"))
            self.cancel_map[transaction.match_type](
                self, cr, uid, transaction.id, context)
            self._legacy_clear_up_writeoff(
                cr, uid, transaction, context=context
            )
        return True

    confirm_map = {
        'invoice': _confirm_move,
        'manual': _confirm_move,
        'move': _confirm_move,
    }

    def confirm(self, cr, uid, ids, context=None):
        if ids and isinstance(ids, (int, float)):
            ids = [ids]
        for transaction in self.browse(cr, uid, ids, context):
            if not transaction.match_type:
                continue
            if transaction.match_type not in self.confirm_map:
                raise orm.except_orm(
                    _("Cannot reconcile"),
                    _("Cannot reconcile type %s. No method found to " +
                      "reconcile this type") %
                    transaction.match_type
                )
            if (transaction.residual and transaction.writeoff_account_id):
                if transaction.match_type not in ('invoice', 'move', 'manual'):
                    raise orm.except_orm(
                        _("Cannot reconcile"),
                        _("Bank transaction %s: write off not implemented for "
                          "this match type.") %
                        transaction.statement_line_id.name
                    )
            # Generalize this bit and move to the confirmation
            # methods that actually do create a voucher?
            self.confirm_map[transaction.match_type](
                self, cr, uid, transaction.id, context)

        return True

    signal_duplicate_keys = [
        # does not include float values
        # such as transferred_amount
        'execution_date', 'local_account', 'remote_account',
        'remote_owner', 'reference', 'message',
    ]

    def create(self, cr, uid, vals, context=None):
        """
        Search for duplicates of the newly created transaction
        and mark them as such unless a context key
        'transaction_no_duplicate_search' is defined and true.
        """
        res = super(banking_import_transaction, self).create(
            cr, uid, vals, context)
        if res and not context.get('transaction_no_duplicate_search'):
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
                raise orm.except_orm(_('Cannot check for duplicate'),
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
                       partial=False, match_type=False, context=None):
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
        move_lines = self.pool.get('account.move.line').browse(
            cr, uid, move_line_ids, context=context
        )
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
            retval['invoice_ids'] = list(set(x.invoice.id for x in move_lines))
            retval['type'] = type_map[move_lines[0].invoice.type]
        return retval

    def move_info2values(self, move_info):
        vals = {}
        vals['match_type'] = move_info['match_type']
        vals['move_line_ids'] = [(6, 0, move_info.get('move_line_ids') or [])]
        vals['invoice_ids'] = [(6, 0, move_info.get('invoice_ids') or [])]
        vals['move_line_id'] = (move_info.get('move_line_ids', False) and
                                len(move_info['move_line_ids']) == 1 and
                                move_info['move_line_ids'][0])
        if move_info['match_type'] == 'invoice':
            vals['invoice_id'] = (move_info.get('invoice_ids', False) and
                                  len(move_info['invoice_ids']) == 1 and
                                  move_info['invoice_ids'][0])
        return vals

    def hook_match_payment(self, cr, uid, transaction, log, context=None):
        """
        To override in module 'account_banking_payment'
        """
        return False

    def match(self, cr, uid, ids, results=None, context=None):
        if not ids:
            return True

        company_obj = self.pool.get('res.company')
        partner_bank_obj = self.pool.get('res.partner.bank')
        journal_obj = self.pool.get('account.journal')
        move_line_obj = self.pool.get('account.move.line')
        payment_line_obj = self.pool.get('payment.line')
        has_payment = bool(
            payment_line_obj and 'date_done' in payment_line_obj._columns)
        statement_line_obj = self.pool.get('account.bank.statement.line')
        statement_obj = self.pool.get('account.bank.statement')
        imported_statement_ids = []

        # Results
        if results is None:
            results = dict(
                trans_loaded_cnt=0,
                trans_skipped_cnt=0,
                trans_matched_cnt=0,
                bank_costs_invoice_cnt=0,
                error_cnt=0,
                log=[],
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
        if has_payment:
            payment_line_ids = payment_line_obj.search(
                cr, uid, [
                    ('order_id.state', '=', 'sent'),
                    ('date_done', '=', False)
                ], context=context)
            payment_lines = payment_line_obj.browse(
                cr, uid, payment_line_ids)

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

            if transaction.local_account in error_accounts:
                results['trans_skipped_cnt'] += 1
                if not injected:
                    i += 1
                continue

            partner_banks = []
            partner_ids = []

            # TODO: optimize by ordering transactions per company,
            # and perform the stanza below only once per company.
            # In that case, take newest transaction date into account
            # when retrieving move_line_ids below.
            company = company_obj.browse(
                cr, uid, transaction.company_id.id, context)

            # Get interesting journals once
            # Added type 'general' to capture fund transfers
            journal_ids = journal_obj.search(
                cr, uid, [
                    ('type', 'in', ('general', 'sale', 'purchase',
                                    'purchase_refund', 'sale_refund')),
                    ('company_id', '=', company.id),
                ],
            )
            # Get all unreconciled moves
            move_line_ids = move_line_obj.search(
                cr, uid, [
                    ('reconcile_id', '=', False),
                    ('journal_id', 'in', journal_ids),
                    ('account_id.reconcile', '=', True),
                    ('date', '<=', transaction.execution_date),
                ],
            )
            if move_line_ids:
                move_lines = move_line_obj.browse(cr, uid, move_line_ids)
            else:
                move_lines = []

            # Create fallback currency code
            currency_code = (transaction.local_currency or
                             company.currency_id.name)

            # Check cache for account info/currency
            if transaction.local_account in info and \
               currency_code in info[transaction.local_account]:
                account_info = info[transaction.local_account][currency_code]
            else:
                # Pull account info/currency
                account_info = banktools.get_company_bank_account(
                    self.pool, cr, uid, transaction.local_account,
                    transaction.local_currency, company, results['log']
                )
                if not account_info:
                    results['log'].append(
                        _('Transaction found for unknown account '
                          '%(bank_account)s') %
                        {'bank_account': transaction.local_account}
                    )
                    error_accounts[transaction.local_account] = True
                    results['error_cnt'] += 1
                    if not injected:
                        i += 1
                    continue
                if 'journal_id' not in account_info.keys():
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
                if transaction.local_account not in info:
                    info[transaction.local_account] = {
                        currency_code: account_info
                    }
                else:
                    info[transaction.local_account][currency_code] = (
                        account_info
                    )

            # Link accounting period
            period_id = banktools.get_period(
                self.pool, cr, uid, transaction.execution_date,
                company, results['log'])
            if not period_id:
                results['trans_skipped_cnt'] += 1
                if not injected:
                    i += 1
                continue

            if transaction.statement_line_id:
                if transaction.statement_line_id.state == 'confirmed':
                    raise orm.except_orm(
                        _("Cannot perform match"),
                        _("Cannot perform match on a confirmed transction"))
            else:
                values = {
                    'name': '%s.%s' % (transaction.statement,
                                       transaction.transaction),
                    'date': transaction.execution_date,
                    'amount': transaction.transferred_amount,
                    'statement_id': transaction.statement_id.id,
                    'note': transaction.message,
                    'ref': transaction.reference,
                    'period_id': period_id,
                    'currency': account_info.currency_id.id,
                    'import_transaction_id': transaction.id,
                    'account_id': (
                        transaction.transferred_amount < 0 and
                        account_info.default_credit_account_id.id or
                        account_info.default_debit_account_id.id),
                }
                statement_line_id = statement_line_obj.create(
                    cr, uid, values, context
                )
                results['trans_loaded_cnt'] += 1
                transaction.write({'statement_line_id': statement_line_id})
                transaction.refresh()
                if transaction.statement_id.id not in imported_statement_ids:
                    imported_statement_ids.append(transaction.statement_id.id)

            # Final check: no coercion of currencies!
            if transaction.local_currency \
               and account_info.currency_id.name != transaction.local_currency:
                # TODO: convert currencies?
                results['log'].append(
                    _('transaction %(statement_id)s.%(transaction_id)s for '
                      'account %(bank_account)s uses different currency than '
                      'the defined bank journal.') %
                    {
                        'bank_account': transactions.local_account,
                        'statement_id': transaction.statement,
                        'transaction_id': transaction.transaction,
                    }
                )
                error_accounts[transaction.local_account] = True
                results['error_cnt'] += 1
                if not injected:
                    i += 1
                continue

            # When bank costs are part of transaction itself, split it.
            if (transaction.type != bt.BANK_COSTS and
                    transaction.provision_costs):
                # Create new transaction for bank costs
                cost_id = self.copy(
                    cr, uid, transaction.id,
                    dict(
                        type=bt.BANK_COSTS,
                        transaction='%s-prov' % transaction.transaction,
                        transferred_amount=transaction.provision_costs,
                        remote_currency=transaction.provision_costs_currency,
                        message=transaction.provision_costs_description,
                        parent_id=transaction.id,
                    ),
                    context)

                injected.append(self.browse(cr, uid, cost_id, context))

                # Remove bank costs from current transaction
                # Note that this requires that the transferred_amount
                # includes the bank costs and that the costs itself are
                # signed correctly.
                self.write(
                    cr, uid, transaction.id,
                    dict(
                        transferred_amount=(
                            transaction.transferred_amount -
                            transaction.provision_costs),
                        provision_costs=False,
                        provision_costs_currency=False,
                        provision_costs_description=False,
                    ),
                    context=context)
                # rebrowse the current record after writing
                transaction = self.browse(
                    cr, uid, transaction.id, context=context
                )

            # Match payment and direct debit orders
            move_info_payment = self.hook_match_payment(
                cr, uid, transaction, results['log'], context=context)
            if move_info_payment:
                move_info = move_info_payment

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
            else:
                # Link remote partner, import account when needed
                partner_banks = banktools.get_bank_accounts(
                    self.pool, cr, uid, transaction.remote_account,
                    results['log'], fail=True
                )
                if partner_banks:
                    partner_ids = [x.partner_id.id for x in partner_banks]
                elif transaction.remote_owner:
                    country_id = banktools.get_country_id(
                        self.pool, cr, uid, transaction, context=context)
                    partner_id = banktools.get_partner(
                        self.pool, cr, uid, transaction.remote_owner,
                        transaction.remote_owner_address,
                        transaction.remote_owner_postalcode,
                        transaction.remote_owner_city,
                        country_id, results['log'],
                        context=context)
                    if partner_id:
                        partner_ids = [partner_id]
                        if transaction.remote_account:
                            partner_bank_id = banktools.create_bank_account(
                                self.pool, cr, uid, partner_id,
                                transaction.remote_account,
                                transaction.remote_owner,
                                transaction.remote_owner_address,
                                transaction.remote_owner_city,
                                country_id, bic=transaction.remote_bank_bic,
                                context=context)
                            partner_banks = partner_bank_obj.browse(
                                cr, uid, [partner_bank_id], context=context)

            # Credit means payment... isn't it?
            if (not move_info and
                    transaction.statement_line_id.amount < 0 and
                    payment_lines):
                # Link open payment - if any
                # Note that _match_payment is defined in the
                # account_banking_payment module which should be installed
                # automatically if account_payment is. And if account_payment
                # is not installed, then payment_lines will be empty.
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
                # settings to overrule this.
                bank_partner = (
                    partner_banks[0].partner_id if len(partner_banks) == 1
                    else False)
                if transaction.statement_line_id.amount < 0:
                    if bank_partner:
                        account_id = bank_partner.\
                            def_journal_account_bank_decr()[bank_partner.id]
                    else:
                        account_id = account_info.default_credit_account_id.id
                else:

                    if bank_partner:
                        account_id = bank_partner.\
                            def_journal_account_bank_incr()[bank_partner.id]
                    else:
                        account_id = account_info.default_debit_account_id.id

            values = {'account_id': account_id}
            self_values = {}
            if move_info:
                results['trans_matched_cnt'] += 1
                self_values.update(
                    self.move_info2values(move_info))
                # values['match_type'] = move_info['match_type']
                values['partner_id'] = move_info['partner_id']
                values['partner_bank_id'] = move_info['partner_bank_id']
                values['type'] = move_info['type']
            else:
                values['partner_id'] = values['partner_bank_id'] = False
            if (not values['partner_id'] and partner_ids and
                    len(partner_ids) == 1):
                values['partner_id'] = partner_ids[0]
            if (not values['partner_bank_id'] and partner_banks and
                    len(partner_banks) == 1):
                values['partner_bank_id'] = partner_banks[0].id

            statement_line_obj.write(
                cr, uid, transaction.statement_line_id.id, values, context)
            self.write(cr, uid, transaction.id, self_values, context)
            if not injected:
                i += 1

        # recompute statement end_balance for validation
        if imported_statement_ids:
            statement_obj.button_dummy(
                cr, uid, imported_statement_ids, context=context)

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
        for transaction in self.browse(cr, uid, ids, context):
            if (transaction.statement_line_id.state == 'draft' and
                    not(transaction.move_currency_amount is False)):
                res[transaction.id] = (
                    transaction.move_currency_amount -
                    transaction.statement_line_id.amount
                )
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
        return res

    def clear_and_write(self, cr, uid, ids, vals=None, context=None):
        """
        Write values in argument 'vals', but clear all match
        related values first
        """
        write_vals = dict(
            [
                (x, False)
                for x in [
                    'match_type',
                    'move_line_id',
                    'invoice_id',
                ]
            ] +
            [
                (x, [(6, 0, [])])
                for x in [
                    'move_line_ids',
                    'invoice_ids',
                ]
            ]
        )
        write_vals.update(vals or {})
        return self.write(cr, uid, ids, write_vals, context=context)

    def _get_move_amount(self, cr, uid, ids, name, args, context=None):
        """
        Need to get the residual amount on the move (invoice) in the bank
        statement currency.
        This will be used to calculate the write-off amount
        (in statement currency).
        """
        if not ids:
            return {}
        res = dict([(x, False) for x in ids])

        stline_pool = self.pool.get('account.bank.statement.line')

        for transaction in self.browse(cr, uid, ids, context):

            if transaction.move_line_id:
                move_line_amount = (
                    transaction.move_line_id.amount_residual_currency)
                statement = transaction.statement_line_id.statement_id
                to_curr_id = (
                    statement.journal_id.currency and
                    statement.journal_id.currency.id or
                    statement.company_id.currency_id.id
                )
                from_curr_id = (
                    transaction.move_line_id.currency_id and
                    transaction.move_line_id.currency_id.id or
                    statement.company_id.currency_id.id
                )
                if from_curr_id != to_curr_id:
                    amount_currency = stline_pool._convert_currency(
                        cr, uid, from_curr_id, to_curr_id, move_line_amount,
                        round=True, date=transaction.statement_line_id.date,
                        context=context
                    )
                else:
                    amount_currency = move_line_amount
                sign = 1
                if transaction.move_line_id.currency_id:
                    if transaction.move_line_id.amount_currency < 0:
                        sign = -1
                else:
                    if (transaction.move_line_id.debit -
                            transaction.move_line_id.credit) < 0:
                        sign = -1
                res[transaction.id] = sign * amount_currency

        return res

    def unlink(self, cr, uid, ids, context=None):
        """
        Unsplit if this if a split transaction
        """
        for this in self.browse(cr, uid, ids, context):
            if this.parent_id:
                this.parent_id.write(
                    {
                        'transferred_amount':
                        this.parent_id.transferred_amount +
                        this.transferred_amount,
                    }
                )
                this.parent_id.refresh()
        return super(banking_import_transaction, self).unlink(
            cr, uid, ids, context=context)

    column_map = {
        # used in bank_import.py, converting non-osv transactions
        'statement_id': 'statement',
        'id': 'transaction'
    }

    _columns = {
        # start mem_bank_transaction atributes
        # see parsers/models.py
        'transaction': fields.char('transaction', size=16),  # id
        'statement': fields.char('statement', size=16),  # statement_id
        'type': fields.char('type', size=16),
        'reference': fields.char('reference', size=1024),
        'local_account': fields.char('local_account', size=24),
        'local_currency': fields.char('local_currency', size=16),
        'execution_date': fields.date('Posted date'),
        'value_date': fields.date('Value date'),
        'remote_account': fields.char('remote_account'),
        'remote_currency': fields.char('remote_currency', size=16),
        'exchange_rate': fields.float('exchange_rate'),
        'transferred_amount': fields.float('transferred_amount'),
        'message': fields.char('message', size=1024),
        'remote_owner': fields.char('remote_owner', size=128),
        'remote_owner_address': fields.char('remote_owner_address', size=256),
        'remote_owner_city': fields.char('remote_owner_city', size=128),
        'remote_owner_postalcode': fields.char(
            'remote_owner_postalcode',
            size=24,
        ),
        'remote_owner_country_code': fields.char(
            'remote_owner_country_code',
            size=24,
        ),
        'remote_owner_custno': fields.char('remote_owner_custno', size=24),
        'remote_bank_bic': fields.char('remote_bank_bic', size=24),
        'remote_bank_bei': fields.char('remote_bank_bei', size=24),
        'remote_bank_ibei': fields.char('remote_bank_ibei', size=24),
        'remote_bank_eangl': fields.char('remote_bank_eangln', size=24),
        'remote_bank_chips_uid': fields.char('remote_bank_chips_uid', size=24),
        'remote_bank_duns': fields.char('remote_bank_duns', size=24),
        'remote_bank_tax_id': fields.char('remote_bank_tax_id', size=24),
        'provision_costs': fields.float('provision_costs', size=24),
        'provision_costs_currency': fields.char(
            'provision_costs_currency',
            size=64,
        ),
        'provision_costs_description': fields.char(
            'provision_costs_description',
            size=24,
        ),
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
            ondelete='cascade'),
        'statement_id': fields.many2one(
            'account.bank.statement', 'Statement',
            ondelete='CASCADE'),
        'parent_id': fields.many2one(
            'banking.import.transaction', 'Split off from this transaction'),
        # match fields
        'match_type': fields.selection([
            ('move', 'Move'),
            ('invoice', 'Invoice'),
            ('payment', 'Payment line'),
            ('payment_order', 'Payment order'),
            ('storno', 'Storno'),
            ('manual', 'Manual'),
            ('payment_manual', 'Payment line (manual)'),
            ('payment_order_manual', 'Payment order (manual)'),
        ], 'Match type'),
        'match_multi': fields.function(
            _get_match_multi, method=True, string='Multi match',
            type='boolean'),
        'move_line_ids': fields.many2many(
            'account.move.line', 'banking_transaction_move_line_rel',
            'move_line_id', 'transaction_id', 'Matching entries'),
        'move_line_id': fields.many2one(
            'account.move.line', 'Entry to reconcile'),
        'invoice_ids': fields.many2many(
            'account.invoice', 'banking_transaction_invoice_rel',
            'invoice_id', 'transaction_id', 'Matching invoices'),
        'invoice_id': fields.many2one(
            'account.invoice', 'Invoice to reconcile'),
        'residual': fields.function(
            _get_residual, method=True, string='Residual', type='float'),
        'writeoff_account_id': fields.many2one(
            'account.account',
            'Write-off account',
            domain=[('type', '!=', 'view')]
        ),
        'payment_option': fields.selection(
            [
                ('without_writeoff', 'Keep Open'),
                ('with_writeoff', 'Reconcile Payment Balance')
            ],
            'Payment Difference',
            required=True,
            help=("This field helps you to choose what you want to do with "
                  "the eventual difference between the paid amount and the "
                  "sum of allocated amounts. You can either choose to keep "
                  "open this difference on the partner's account, "
                  "or reconcile it with the payment(s)"),
        ),
        'writeoff_amount': fields.float('Difference Amount'),
        # Legacy field: to be removed after 7.0
        'writeoff_move_line_id': fields.many2one(
            'account.move.line', 'Write off move line'),
        'writeoff_analytic_id': fields.many2one(
            'account.analytic.account', 'Write off analytic account'),
        'move_currency_amount': fields.function(
            _get_move_amount,
            method=True,
            string='Match Amount',
            type='float',
        ),
    }

    _defaults = {
        'company_id': lambda s, cr, uid, c:
            s.pool.get('res.company')._company_default_get(
                cr, uid, 'bank.import.transaction', context=c),
        'payment_option': 'without_writeoff',
    }


class account_bank_statement_line(orm.Model):
    _inherit = 'account.bank.statement.line'

    def _get_link_partner_ok(
            self, cr, uid, ids, name, args, context=None):
        """
        Deliver the values of the function field that
        determines if the 'link partner' wizard is show on the
        bank statement line
        """
        res = {}
        for line in self.browse(cr, uid, ids, context):
            res[line.id] = bool(
                line.state == 'draft' and not line.partner_id and
                line.import_transaction_id and
                line.import_transaction_id.remote_account)
        return res

    _columns = {
        'import_transaction_id': fields.many2one(
            'banking.import.transaction',
            'Import transaction', readonly=True, ondelete='cascade'),
        'match_multi': fields.related(
            'import_transaction_id', 'match_multi', type='boolean',
            string='Multi match', readonly=True),
        'residual': fields.related(
            'import_transaction_id', 'residual', type='float',
            string='Residual', readonly=True,
        ),
        'duplicate': fields.related(
            'import_transaction_id', 'duplicate', type='boolean',
            string='Possible duplicate import', readonly=True),
        'match_type': fields.related(
            'import_transaction_id', 'match_type', type='selection',
            selection=[
                ('move', 'Move'),
                ('invoice', 'Invoice'),
                ('payment', 'Payment line'),
                ('payment_order', 'Payment order'),
                ('storno', 'Storno'),
                ('manual', 'Manual'),
                ('payment_manual', 'Payment line (manual)'),
                ('payment_order_manual', 'Payment order (manual)'),
            ],
            string='Match type', readonly=True,),
        'state': fields.selection(
            [('draft', 'Draft'), ('confirmed', 'Confirmed')], 'State',
            readonly=True, required=True),
        'parent_id': fields.many2one(
            'account.bank.statement.line',
            'Parent',
        ),
        'link_partner_ok': fields.function(
            _get_link_partner_ok, type='boolean',
            string='Can link partner'),
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
            res = wizard_obj.create_act_window(
                cr, uid, res_id, context=context
            )
        return res

    def link_partner(self, cr, uid, ids, context=None):
        """
        Get the appropriate partner or fire a wizard to create
        or link one
        """
        if not ids:
            return False

        if isinstance(ids, (int, long)):
            ids = [ids]

        # Check if the partner is already known but not shown
        # because the screen was not refreshed yet
        statement_line = self.browse(
            cr, uid, ids[0], context=context)
        if statement_line.partner_id:
            return True

        # Reuse the bank's partner if any
        if (statement_line.partner_bank_id and
                statement_line.partner_bank_id.partner_id):
            statement_line.write(
                {'partner_id': statement_line.partner_bank_id.partner_id.id})
            return True

        if (not statement_line.import_transaction_id or
                not statement_line.import_transaction_id.remote_account):
            raise orm.except_orm(
                _("Error"),
                _("No bank account available to link partner to"))

        # Check if the bank account was already been linked
        # manually to another transaction
        remote_account = statement_line.import_transaction_id.remote_account
        source_line_ids = self.search(
            cr, uid,
            [('import_transaction_id.remote_account', '=', remote_account),
             ('partner_bank_id.partner_id', '!=', False),
             ], limit=1, context=context)
        if source_line_ids:
            source_line = self.browse(
                cr, uid, source_line_ids[0], context=context)
            target_line_ids = self.search(
                cr, uid,
                [('import_transaction_id.remote_account', '=', remote_account),
                 ('partner_bank_id', '=', False),
                 ('state', '=', 'draft')], context=context)
            self.write(
                cr, uid, target_line_ids,
                {'partner_bank_id': source_line.partner_bank_id.id,
                 'partner_id': source_line.partner_bank_id.partner_id.id,
                 }, context=context)
            return True

        # Or fire the wizard to link partner and account
        wizard_obj = self.pool.get('banking.link_partner')
        res_id = wizard_obj.create(
            cr, uid, {'statement_line_id': ids[0]}, context=context)
        return wizard_obj.create_act_window(cr, uid, res_id, context=context)

    def _convert_currency(
            self, cr, uid, from_curr_id, to_curr_id, from_amount,
            round=False, date=None, context=None):
        """Convert currency amount using the company rate on a specific date"""
        curr_obj = self.pool.get('res.currency')
        if context:
            ctxt = context.copy()
        else:
            ctxt = {}
        if date:
            ctxt["date"] = date

        amount = curr_obj.compute(
            cr, uid, from_curr_id, to_curr_id, from_amount,
            round=round, context=ctxt)
        return amount

    def confirm(self, cr, uid, ids, context=None):
        """
        Create (or update) a voucher for each statement line, and then generate
        the moves by posting the voucher.
        If a line does not have a move line against it, but has an account,
        then generate a journal entry that moves the line amount to the
        specified account.
        """
        statement_pool = self.pool.get('account.bank.statement')
        obj_seq = self.pool.get('ir.sequence')
        import_transaction_obj = self.pool.get('banking.import.transaction')

        for st_line in self.browse(cr, uid, ids, context):
            if st_line.state != 'draft':
                continue
            if st_line.duplicate:
                raise orm.except_orm(
                    _('Bank transfer flagged as duplicate'),
                    _("You cannot confirm a bank transfer marked as a "
                      "duplicate (%s.%s)") %
                    (st_line.statement_id.name, st_line.name,))
            if st_line.analytic_account_id:
                if not st_line.statement_id.journal_id.analytic_journal_id:
                    raise orm.except_orm(
                        _('No Analytic Journal !'),
                        _("You have to define an analytic journal on the '%s' "
                          "journal!") % st_line.statement_id.journal_id.name
                    )
            if not st_line.amount:
                continue
            if not st_line.period_id:
                self.write(
                    cr, uid, [st_line.id],
                    {
                        'period_id': self._get_period(
                            cr, uid, date=st_line.date, context=context)
                    })
                st_line.refresh()
            # Generate the statement number, if it is not already done
            st = st_line.statement_id
            if not st.name == '/':
                st_number = st.name
            else:
                if st.journal_id.sequence_id:
                    period = st.period_id or st_line.period_id
                    c = {'fiscalyear_id': period.fiscalyear_id.id}
                    st_number = obj_seq.next_by_id(
                        cr, uid, st.journal_id.sequence_id.id, context=c
                    )
                else:
                    st_number = obj_seq.next_by_code(
                        cr, uid, 'account.bank.statement'
                    )
                statement_pool.write(
                    cr, uid, [st.id], {'name': st_number}, context=context
                )

            if st_line.import_transaction_id:
                import_transaction_obj.confirm(
                    cr, uid, st_line.import_transaction_id.id, context)
            st_line.refresh()
            st_line_number = statement_pool.get_next_st_line_number(
                cr, uid, st_number, st_line, context)
            company_currency_id = st.journal_id.company_id.currency_id.id
            statement_pool.create_move_from_st_line(
                cr, uid, st_line.id, company_currency_id, st_line_number,
                context
            )
            self.write(
                cr, uid, st_line.id, {'state': 'confirmed'}, context)
        return True

    def cancel(self, cr, uid, ids, context=None):
        if ids and isinstance(ids, (int, float)):
            ids = [ids]
        import_transaction_obj = self.pool.get('banking.import.transaction')
        move_pool = self.pool.get('account.move')
        set_draft_ids = []
        move_unlink_ids = []
        # harvest ids for various actions
        for st_line in self.browse(cr, uid, ids, context):
            if st_line.state != 'confirmed':
                continue
            if st_line.statement_id.state != 'draft':
                raise orm.except_orm(
                    _("Cannot cancel bank transaction"),
                    _("The bank statement that this transaction belongs to "
                      "has already been confirmed"))

            if st_line.import_transaction_id:
                # Cancel transaction immediately.
                # If it has voucher, this will clean up
                # the moves on the st_line.
                import_transaction_obj.cancel(
                    cr, uid, [st_line.import_transaction_id.id],
                    context=context
                )
            st_line.refresh()
            for line in st_line.move_ids:
                # We allow for people canceling and removing
                # the associated payments, which can lead to confirmed
                # statement lines without an associated move
                move_unlink_ids.append(line.id)
            set_draft_ids.append(st_line.id)

        move_pool.button_cancel(
            cr, uid, move_unlink_ids, context=context)
        move_pool.unlink(cr, uid, move_unlink_ids, context=context)
        self.write(
            cr, uid, set_draft_ids, {'state': 'draft'}, context=context)
        return True

    def unlink(self, cr, uid, ids, context=None):
        """
        Don't allow deletion of a confirmed statement line
        If this statement line comes from a split transaction, give the
        amount back
        """
        if type(ids) is int:
            ids = [ids]
        for line in self.browse(cr, uid, ids, context=context):
            if line.state == 'confirmed':
                raise orm.except_orm(
                    _('Confirmed Statement Line'),
                    _("You cannot delete a confirmed Statement Line"
                      ": '%s'") % line.name)
            if line.parent_id:
                line.parent_id.write(
                    {
                        'amount': line.parent_id.amount + line.amount,
                    }
                )
                line.parent_id.refresh()
        return super(account_bank_statement_line, self).unlink(
            cr, uid, ids, context=context)

    def create_instant_transaction(self, cr, uid, ids, context=None):
        """
        Check for existance of import transaction on the
        bank statement lines. Create instant items if appropriate.

        This way, the matching wizard works on manually
        encoded statements.

        The transaction is only filled with the most basic
        information. The use of the transaction at this point
        is rather to store matching data rather than to
        provide data about the transaction which have all been
        transferred to the bank statement line.
        """
        import_transaction_pool = self.pool.get('banking.import.transaction')
        if ids and isinstance(ids, (int, long)):
            ids = [ids]
        if context is None:
            context = {}
        localcontext = context.copy()
        localcontext['transaction_no_duplicate_search'] = True
        for line in self.browse(cr, uid, ids, context=context):
            if line.state != 'confirmed' and not line.import_transaction_id:
                res = import_transaction_pool.create(
                    cr, uid,
                    {
                        'company_id': line.statement_id.company_id.id,
                        'statement_line_id': line.id,
                    },
                    context=localcontext)
                self.write(
                    cr, uid, line.id,
                    {
                        'import_transaction_id': res
                    },
                    context=context)

    def split_off(self, cr, uid, ids, amount, context=None):
        """
        Create a child statement line with amount, deduce that from this line,
        change transactions accordingly
        """
        if context is None:
            context = {}

        transaction_pool = self.pool.get('banking.import.transaction')

        child_statement_ids = []
        for this in self.browse(cr, uid, ids, context):
            transaction_data = transaction_pool.copy_data(
                cr, uid, this.import_transaction_id.id
            )
            transaction_data['transferred_amount'] = amount
            transaction_data['message'] = (
                (transaction_data['message'] or '') + _(' (split)'))
            transaction_data['parent_id'] = this.import_transaction_id.id
            transaction_id = transaction_pool.create(
                cr,
                uid,
                transaction_data,
                context=dict(context, transaction_no_duplicate_search=True)
            )

            statement_line_data = self.copy_data(cr, uid, this.id)
            statement_line_data['amount'] = amount
            statement_line_data['name'] = (
                (statement_line_data['name'] or '') + _(' (split)'))
            statement_line_data['import_transaction_id'] = transaction_id
            statement_line_data['parent_id'] = this.id
            statement_line_id = self.create(
                cr, uid, statement_line_data, context=context)

            child_statement_ids.append(statement_line_id)
            transaction_pool.write(
                cr, uid, transaction_id,
                {
                    'statement_line_id': statement_line_id,
                },
                context=context)
            this.write({'amount': this.amount - amount})

        return child_statement_ids


class account_bank_statement(orm.Model):
    _inherit = 'account.bank.statement'

    def _end_balance(self, cr, uid, ids, name, attr, context=None):
        """
        This method taken from account/account_bank_statement.py and
        altered to take the statement line subflow into account
        """
        res = {}

        statements = self.browse(cr, uid, ids, context=context)
        for statement in statements:
            res[statement.id] = statement.balance_start

            # Calculate the balance based on the statement line amounts
            # ..they are in the statement currency, no conversion needed.
            for line in statement.line_ids:
                res[statement.id] += line.amount

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
            if not self.check_status_condition(
                    cr, uid, st.state, journal_type=j_type):
                continue

            self.balance_check(cr, uid, st.id, journal_type=j_type,
                               context=context)
            if (not st.journal_id.default_credit_account_id) \
                    or (not st.journal_id.default_debit_account_id):
                raise orm.except_orm(
                    _('Configuration Error'),
                    _('Please verify that an account is defined in the '
                      'journal.')
                )

            # protect against misguided manual changes
            for line in st.move_line_ids:
                if line.state != 'valid':
                    raise orm.except_orm(
                        _('Error'),
                        _('The account entries lines are not in valid state.')
                    )

            line_obj.confirm(cr, uid, [line.id for line in st.line_ids],
                             context)
            st.refresh()
            self.message_post(
                cr, uid, [st.id],
                body=_('Statement %s confirmed, journal items were created.')
                % (st.name,), context=context)
        return self.write(cr, uid, ids, {'state': 'confirm'}, context=context)

    def button_cancel(self, cr, uid, ids, context=None):
        """
        Do nothing but write the state. Delegate all actions to the statement
        line workflow instead.
        """
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def unlink(self, cr, uid, ids, context=None):
        """
        Don't allow deletion of statement with confirmed bank statement lines.
        """
        if type(ids) is int:
            ids = [ids]
        for st in self.browse(cr, uid, ids, context=context):
            for line in st.line_ids:
                if line.state == 'confirmed':
                    raise orm.except_orm(
                        _('Confirmed Statement Lines'),
                        _("You cannot delete a Statement with confirmed "
                          "Statement Lines: '%s'") % st.name)
        return super(account_bank_statement, self).unlink(
            cr, uid, ids, context=context)

    _columns = {
        # override this field *only* to replace the
        # function method with the one from this module.
        # Note that it is defined twice, both in
        # account/account_bank_statement.py (without 'store') and
        # account/account_cash_statement.py (with store=True)

        'balance_end': fields.function(
            _end_balance, method=True, store=True, string='Balance'),
    }
