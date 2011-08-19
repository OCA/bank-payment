# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
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
# Many thanks to our contributors
#
# Kaspars Vilkens (KNdati): lenghty discussions, bugreports and bugfixes
# Stefan Rijnhart (Therp): bugreport and bugfix
#
'''
This module contains the business logic of the wizard account_banking_import.
The parsing is done in the parser modules. Every parser module is required to
use parser.models as a mean of communication with the business logic.
'''
from osv import osv, fields
import time
import netsvc
import base64
import datetime
from tools import config
from tools.translate import _
from account_banking.parsers import models
from account_banking.parsers.convert import *
from account_banking.struct import struct
from account_banking import sepa
from banktools import *
import decimal_precision as dp

bt = models.mem_bank_transaction

# This variable is used to match supplier invoices with an invoice date after
# the real payment date. This can occur with online transactions (web shops).
payment_window = datetime.timedelta(days=10)

def parser_types(*args, **kwargs):
    '''Delay evaluation of parser types until start of wizard, to allow
       depending modules to initialize and add their parsers to the list
    '''
    return models.parser_type.get_parser_types()

class banking_import(osv.osv_memory):
    _name = 'account.banking.bank.import'

    def _get_move_info(self, cursor, uid, move_line, partner_bank_id=False,
                       partial=False):
        reconcile_obj = self.pool.get('account.move.reconcile')
        type_map = {
            'out_invoice': 'customer',
            'in_invoice': 'supplier',
            'out_refund': 'customer',
            'in_refund': 'supplier',
        }
        retval = struct(move_line=move_line, partner_id=move_line.partner_id.id,
                        partner_bank_id=partner_bank_id,
                        reference=move_line.ref
                       )
        if move_line.invoice:
            retval.invoice = move_line.invoice
            retval.type = type_map[move_line.invoice.type]
        else:
            retval.type = 'general'

        if partial:
            move_line.reconcile_partial_id = reconcile_obj.create(
                cursor, uid, {
                    'type': 'auto',
                    'line_partial_ids': [(4, 0, [move_line.id])]
                    }
            )
        else:
            if move_line.reconcile_partial_id:
                partial_ids = [x.id for x in
                               move_line.reconcile_partial_id.line_partial_ids
                              ]
            else:
                partial_ids = []
            move_line.reconcile_id = reconcile_obj.create(
                cursor, uid, {
                    'type': 'auto',
                    'line_id': [
                        (4, x, False) for x in [move_line.id] + partial_ids
                    ],
                    'line_partial_ids': [
                        (3, x, False) for x in partial_ids
                    ]
                }
            )
        return retval

    def _link_payment(self, cursor, uid, trans, payment_lines,
                      partner_ids, bank_account_ids, log, linked_payments):
        '''
        Find the payment order belonging to this reference - if there is one
        This is the easiest part: when sending payments, the returned bank info
        should be identical to ours.
        '''
        # TODO: Not sure what side effects are created when payments are done
        # for credited customer invoices, which will be matched later on too.
        digits = dp.get_precision('Account')(cursor)[1]
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
                payment_line_obj = self.pool.get('payment.line')
                payment_line_obj.write(cursor, uid, [candidate.id], {
                    'export_state': 'done',
                    'date_done': trans.effective_date.strftime('%Y-%m-%d')}
                )
                
                return self._get_move_info(cursor, uid, candidate.move_line_id)

        return False

    def _link_invoice(self, cursor, uid, trans, move_lines,
                      partner_ids, bank_account_ids, log, linked_invoices):
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

        Return values:
            move_info: the move_line information belonging to the matched
                       invoice
            new_trans: the new transaction when the current one was split.
            This can happen when multiple invoices were paid with a single
            bank transaction.
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

        digits = dp.get_precision('Account')(cursor)[1]
        partial = False

        # Search invoice on partner
        if partner_ids:
            candidates = [x for x in move_lines
                          if x.partner_id.id in partner_ids and
                          str2date(x.date, '%Y-%m-%d') <= (trans.execution_date + payment_window)
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
            candidates = [x for x in candidates or move_lines 
                          if x.invoice and has_id_match(x.invoice, ref, msg)
                              and str2date(x.invoice.date_invoice, '%Y-%m-%d')
                                <= (trans.execution_date + payment_window)
                              and (not _cached(x) or _remaining(x))
                         ]

        # Match on amount expected. Limit this kind of search to known
        # partners.
        if not candidates and partner_ids:
            candidates = [x for x in move_lines 
                          if round(abs(x.credit or x.debit), digits) == 
                                round(abs(trans.transferred_amount), digits)
                              and str2date(x.date, '%Y-%m-%d') <=
                                (trans.execution_date + payment_window)
                              and (not _cached(x) or _remaining(x))
                         ]

        move_line = False
        if candidates and len(candidates) > 0:
            # Now a possible selection of invoices has been found, check the
            # amounts expected and received.
            #
            # TODO: currency coercing
            best = [x for x in candidates
                    if round(abs(x.credit or x.debit), digits) == 
                          round(abs(trans.transferred_amount), digits)
                        and str2date(x.date, '%Y-%m-%d') <=
                          (trans.execution_date + payment_window)
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
                                <= trans.execution_date
                            and (_cached(x) and not _remaining(x))
                       ]
                if paid:
                    log.append(
                        _('Unable to link transaction id %(trans)s '
                          '(ref: %(ref)s) to invoice: '
                          'invoice %(invoice)s was already paid') % {
                              'trans': '%s.%s' % (trans.statement_id, trans.id),
                              'ref': trans.reference,
                              'invoice': eyecatcher(paid[0].invoice)
                          })
                else:
                    # Multiple matches
                    log.append(
                        _('Unable to link transaction id %(trans)s (ref: %(ref)s) to invoice: '
                          '%(no_candidates)s candidates found; can\'t choose.') % {
                              'trans': '%s.%s' % (trans.statement_id, trans.id),
                              'ref': trans.reference,
                              'no_candidates': len(best) or len(candidates)
                          })
                    log.append('    ' +
                        _('Candidates: %(candidates)s') % {
                              'candidates': ', '.join([x.invoice.number
                                                       for x in best or candidates
                                                      ])
                          })
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
                    invoice_obj = self.pool.get('account.invoice')
                    invoice_obj.write(cursor, uid, [invoice.id], {
                        'state': 'paid'
                    })
                elif abs(expected) > abs(found):
                    # Partial payment, reuse invoice
                    _cache(move_line, expected - found)
                elif abs(expected) < abs(found):
                    # Possible combined payments, need to split transaction to
                    # verify
                    _cache(move_line)
                    trans2 = trans.copy()
                    trans2.transferred_amount -= expected
                    trans.transferred_amount = expected
                    trans.id += 'a'
                    trans2.id += 'b'
                    # NOTE: the following is debatable. By copying the
                    # eyecatcher of the invoice itself, we enhance the
                    # tracability of the invoices, but we degrade the
                    # tracability of the bank transactions. When debugging, it
                    # is wise to disable this line.
                    trans.reference = eyecatcher(move_line.invoice)

        if move_line:
            account_ids = [
                x.id for x in bank_account_ids 
                if x.partner_id.id == move_line.partner_id.id
            ]

            return (
                self._get_move_info(cursor, uid, move_line, 
                    account_ids and account_ids[0] or False,
                    partial=(partial and not trans2)
                    ),
                trans2
            )


        return (False, False)

    def _link_canceled_debit(self, cursor, uid, trans, payment_lines,
                             partner_ids, bank_account_ids, log):
        '''
        Direct debit transfers can be canceled by the remote owner within a
        legaly defined time period. These 'payments' are most likely
        already marked 'done', which makes them harder to match. Also the
        reconciliation has to be reversed.
        '''
        # TODO: code _link_canceled_debit
        return False

    def _link_costs(self, cursor, uid, trans, period_id, account_info, log):
        '''
        Get or create a costs invoice for the bank and return it with
        the payment as seen in the transaction (when not already done).
        '''
        if not account_info.costs_account_id:
            return []

        digits = dp.get_precision('Account')(cursor)[1]
        amount = round(abs(trans.transferred_amount), digits)
        # Make sure to be able to pinpoint our costs invoice for later
        # matching
        reference = '%s.%s: %s' % (trans.statement_id, trans.id, trans.reference)

        # search supplier invoice
        invoice_obj = self.pool.get('account.invoice')
        invoice_ids = invoice_obj.search(cursor, uid, [
            '&',
            ('type', '=', 'in_invoice'),
            ('partner_id', '=', account_info.bank_partner_id.id),
            ('company_id', '=', account_info.company_id.id),
            ('date_invoice', '=', date2str(trans.effective_date)),
            ('reference', '=', reference),
            ('amount_total', '=', amount),
            ]
        )
        if invoice_ids and len(invoice_ids) == 1:
            invoice = invoice_obj.browse(cursor, uid, invoice_ids)[0]
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
                cursor, uid, [account_info.bank_partner_id.id], ['invoice']
            )
            invoice_id = invoice_obj.create(cursor, uid, dict(
                type = 'in_invoice',
                company_id = account_info.company_id.id,
                partner_id = account_info.bank_partner_id.id,
                address_invoice_id = invoice_address_id['invoice'],
                period_id = period_id,
                journal_id = account_info.invoice_journal_id.id,
                account_id = account_info.bank_partner_id.property_account_payable.id,
                date_invoice = date2str(trans.effective_date),
                reference_type = 'none',
                reference = reference,
                name = trans.reference or trans.message,
                check_total = amount,
                invoice_line = invoice_lines,
            ))
            invoice = invoice_obj.browse(cursor, uid, invoice_id)
            # Create workflow
            invoice_obj.button_compute(cursor, uid, [invoice_id], 
                                       {'type': 'in_invoice'}, set_total=True)
            wf_service = netsvc.LocalService('workflow')
            # Move to state 'open'
            wf_service.trg_validate(uid, 'account.invoice', invoice.id,
                                    'invoice_open', cursor)

        # return move_lines to mix with the rest
        return [x for x in invoice.move_id.line_id if x.account_id.reconcile]

    def import_statements_file(self, cursor, uid, ids, context):
        '''
        Import bank statements / bank transactions file.
        This method represents the business logic, the parser modules
        represent the decoding logic.
        '''
        banking_import = self.browse(cursor, uid, ids, context)[0]
        statements_file = banking_import.file
        data = base64.decodestring(statements_file)

        company_obj = self.pool.get('res.company')
        user_obj = self.pool.get('res.user')
        partner_bank_obj = self.pool.get('res.partner.bank')
        journal_obj = self.pool.get('account.journal')
        move_line_obj = self.pool.get('account.move.line')
        payment_line_obj = self.pool.get('payment.line')
        statement_obj = self.pool.get('account.bank.statement')
        statement_line_obj = self.pool.get('account.bank.statement.line')
        statement_file_obj = self.pool.get('account.banking.imported.file')
        payment_order_obj = self.pool.get('payment.order')
        currency_obj = self.pool.get('res.currency')

        # get the parser to parse the file
        parser_code = banking_import.parser
        parser = models.create_parser(parser_code)
        if not parser:
            raise osv.except_osv(
                _('ERROR!'),
                _('Unable to import parser %(parser)s. Parser class not found.') %
                {'parser': parser_code}
            )

        # Get the company
        company = (banking_import.company or
                   user_obj.browse(cursor, uid, uid, context).company_id)

        # Parse the file
        statements = parser.parse(data)

        if any([x for x in statements if not x.is_valid()]):
            raise osv.except_osv(
                _('ERROR!'),
                _('The imported statements appear to be invalid! Check your file.')
            )

        # Create the file now, as the statements need to be linked to it
        import_id = statement_file_obj.create(cursor, uid, dict(
            company_id = company.id,
            file = statements_file,
            state = 'unfinished',
            format = parser.name,
        ))

        # Results
        results = struct(
            stat_loaded_cnt = 0,
            trans_loaded_cnt = 0,
            stat_skipped_cnt = 0,
            trans_skipped_cnt = 0,
            trans_matched_cnt = 0,
            bank_costs_invoice_cnt = 0,
            error_cnt = 0,
            log = [],
        )

        # Caching
        error_accounts = {}
        info = {}
        imported_statement_ids = []
        linked_payments = {}
        linked_invoices = {}

        if statements:
            # Get default defaults
            def_pay_account_id = company.partner_id.property_account_payable.id
            def_rec_account_id = company.partner_id.property_account_receivable.id

            # Get interesting journals once
            journal_ids = journal_obj.search(cursor, uid, [
                ('type', 'in', ('sale','purchase',
                                'purchase_refund','sale_refund')),
                ('company_id', '=', company.id),
            ])
            # Get all unreconciled moves predating the last statement in one big
            # swoop. Assumption: the statements in the file are sorted in ascending
            # order of date.
            move_line_ids = move_line_obj.search(cursor, uid, [
                ('reconcile_id', '=', False),
                ('journal_id', 'in', journal_ids),
                ('account_id.reconcile', '=', True),
                ('date', '<=', date2str(statements[-1].date)),
            ])
            if move_line_ids:
                move_lines = move_line_obj.browse(cursor, uid, move_line_ids)
            else:
                move_lines = []

            # Get all unreconciled sent payment lines in one big swoop.
            # No filtering can be done, as empty dates carry value for C2B
            # communication. Most likely there are much less sent payments
            # than reconciled and open/draft payments.
            cursor.execute("SELECT l.id FROM payment_order o, payment_line l "
                           "WHERE l.order_id = o.id AND "
                                 "o.state = 'sent' AND "
                                 "l.date_done IS NULL"
                          )
            payment_line_ids = [x[0] for x in cursor.fetchall()]
            if payment_line_ids:
                payment_lines = payment_line_obj.browse(cursor, uid, payment_line_ids)
            else:
                payment_lines = []

        for statement in statements:
            if statement.local_account in error_accounts:
                # Don't repeat messages
                results.stat_skipped_cnt += 1
                results.trans_skipped_cnt += len(statement.transactions)
                continue

            # Create fallback currency code
            currency_code = statement.local_currency or company.currency_id.name

            # Check cache for account info/currency
            if statement.local_account in info and \
               currency_code in info[statement.local_account]:
                account_info = info[statement.local_account][currency_code]

            else:
                # Pull account info/currency
                account_info = get_company_bank_account(
                    self.pool, cursor, uid, statement.local_account,
                    statement.local_currency, company, results.log
                )
                if not account_info:
                    results.log.append(
                        _('Statements found for unknown account %(bank_account)s') %
                        {'bank_account': statement.local_account}
                    )
                    error_accounts[statement.local_account] = True
                    results.error_cnt += 1
                    continue
                if 'journal_id' not in account_info:
                    results.log.append(
                        _('Statements found for account %(bank_account)s, '
                          'but no default journal was defined.'
                         ) % {'bank_account': statement.local_account}
                    )
                    error_accounts[statement.local_account] = True
                    results.error_cnt += 1
                    continue

                # Get required currency code
                currency_code = account_info.currency_id.name

                # Cache results
                if not statement.local_account in info:
                    info[statement.local_account] = {
                        currency_code: account_info
                    }
                else:
                    info[statement.local_account][currency_code] = account_info

            # Final check: no coercion of currencies!
            if statement.local_currency \
               and account_info.currency_id.name != statement.local_currency:
                # TODO: convert currencies?
                results.log.append(
                    _('Statement %(statement_id)s for account %(bank_account)s' 
                      ' uses different currency than the defined bank journal.'
                     ) % {
                         'bank_account': statement.local_account,
                         'statement_id': statement.id
                     }
                )
                error_accounts[statement.local_account] = True
                results.error_cnt += 1
                continue

            # Check existence of previous statement
            statement_ids = statement_obj.search(cursor, uid, [
                ('name', '=', statement.id),
                ('date', '=', date2str(statement.date)),
            ])
            if statement_ids:
                results.log.append(
                    _('Statement %(id)s known - skipped') % {
                        'id': statement.id
                    }
                )
                continue

            statement_id = statement_obj.create(cursor, uid, dict(
                name = statement.id,
                journal_id = account_info.journal_id.id,
                date = date2str(statement.date),
                balance_start = statement.start_balance,
                balance_end_real = statement.end_balance,
                balance_end = statement.end_balance,
                state = 'draft',
                user_id = uid,
                banking_id = import_id,
            ))
            imported_statement_ids.append(statement_id)

            # move each transaction to the right period and try to match it with an
            # invoice or payment
            subno = 0
            injected = []
            i = 0
            max_trans = len(statement.transactions)
            while i < max_trans:
                move_info = False
                if injected:
                    # Force FIFO behavior
                    transaction = injected.pop(0)
                else:
                    transaction = statement.transactions[i]
                    # Keep a tracer for identification of order in a statement in case
                    # of missing transaction ids.
                    subno += 1

                # Link accounting period
                period_id = get_period(self.pool, cursor, uid,
                                       transaction.effective_date, company,
                                       results.log)
                if not period_id:
                    results.trans_skipped_cnt += 1
                    if not injected:
                        i += 1
                    continue

                # When bank costs are part of transaction itself, split it.
                if transaction.type != bt.BANK_COSTS and transaction.provision_costs:
                    # Create new transaction for bank costs
                    costs = transaction.copy()
                    costs.type = bt.BANK_COSTS
                    costs.id = '%s-prov' % transaction.id
                    costs.transferred_amount = transaction.provision_costs
                    costs.remote_currency = transaction.provision_costs_currency
                    costs.message = transaction.provision_costs_description
                    injected.append(costs)

                    # Remove bank costs from current transaction
                    # Note that this requires that the transferred_amount
                    # includes the bank costs and that the costs itself are
                    # signed correctly.
                    transaction.transferred_amount -= transaction.provision_costs
                    transaction.provision_costs = None
                    transaction.provision_costs_currency = None
                    transaction.provision_costs_description = None

                # Allow inclusion of generated bank invoices
                if transaction.type == bt.BANK_COSTS:
                    lines = self._link_costs(
                        cursor, uid, transaction, period_id, account_info,
                        results.log
                    )
                    results.bank_costs_invoice_cnt += bool(lines)
                    for line in lines:
                        if not [x for x in move_lines if x.id == line.id]:
                            move_lines.append(line)
                    partner_ids = [account_info.bank_partner_id.id]
                    partner_banks = []

                else:
                    # Link remote partner, import account when needed
                    partner_banks = get_bank_accounts(
                        self.pool, cursor, uid, transaction.remote_account,
                        results.log, fail=True
                    )
                    if partner_banks:
                        partner_ids = [x.partner_id.id for x in partner_banks]
                    elif transaction.remote_owner:
                        iban = sepa.IBAN(transaction.remote_account)
                        if iban.valid:
                            country_code = iban.countrycode
                        elif transaction.remote_owner_country_code:
                            country_code = transaction.remote_owner_country_code
                        elif hasattr(parser, 'country_code') and parser.country_code:
                            country_code = parser.country_code
                        else:
                            country_code = None
                        partner_id = get_or_create_partner(
                            self.pool, cursor, uid, transaction.remote_owner,
                            transaction.remote_owner_address,
                            transaction.remote_owner_postalcode,
                            transaction.remote_owner_city,
                            country_code, results.log
                        )
                        if transaction.remote_account:
                            partner_bank_id = create_bank_account(
                                self.pool, cursor, uid, partner_id,
                                transaction.remote_account,
                                transaction.remote_owner, 
                                transaction.remote_owner_address,
                                transaction.remote_owner_city,
                                country_code, results.log
                            )
                            partner_banks = partner_bank_obj.browse(
                                cursor, uid, [partner_bank_id]
                            )
                        else:
                            partner_bank_id = None
                            partner_banks = []
                        partner_ids = [partner_id]
                    else:
                        partner_ids = []
                        partner_banks = []

                # Credit means payment... isn't it?
                if transaction.transferred_amount < 0 and payment_lines:
                    # Link open payment - if any
                    move_info = self._link_payment(
                        cursor, uid, transaction,
                        payment_lines, partner_ids,
                        partner_banks, results.log, linked_payments,
                        )

                # Second guess, invoice -> may split transaction, so beware
                if not move_info:
                    # Link invoice - if any. Although bank costs are not an
                    # invoice, automatic invoicing on bank costs will create
                    # these, and invoice matching still has to be done.
                    move_info, remainder = self._link_invoice(
                        cursor, uid, transaction, move_lines, partner_ids,
                        partner_banks, results.log, linked_invoices,
                        )
                    if remainder:
                        injected.append(remainder)

                if not move_info:
                    # Use the default settings, but allow individual partner
                    # settings to overrule this. Note that you need to change
                    # the internal type of these accounts to either 'payable'
                    # or 'receivable' to enable usage like this.
                    if transaction.transferred_amount < 0:
                        if len(partner_banks) == 1:
                            account_id = partner_banks[0].partner_id.property_account_payable
                        if len(partner_banks) != 1 or not account_id or account_id.id == def_pay_account_id:
                            account_id = account_info.default_credit_account_id
                    else:
                        if len(partner_banks) == 1:
                            account_id = partner_banks[0].partner_id.property_account_receivable
                        if len(partner_banks) != 1 or not account_id or account_id.id == def_rec_account_id:
                            account_id = account_info.default_debit_account_id
                else:
                    account_id = move_info.move_line.account_id
                    results.trans_matched_cnt += 1

                values = struct(
                    name = '%s.%s' % (statement.id, transaction.id or subno),
                    date = transaction.effective_date,
                    amount = transaction.transferred_amount,
                    account_id = account_id.id,
                    statement_id = statement_id,
                    note = transaction.message,
                    ref = transaction.reference,
                    period_id = period_id,
                    currency = account_info.currency_id.id,
                )
                if move_info:
                    values.type = move_info.type
                    values.reconcile_id = move_info.move_line.reconcile_id
                    values.partner_id = move_info.partner_id
                    values.partner_bank_id = move_info.partner_bank_id
                else:
                    values.partner_id = values.partner_bank_id = False
                if not values.partner_id and partner_ids and len(partner_ids) == 1:
                    values.partner_id = partner_ids[0]
                if not values.partner_bank_id and partner_banks and \
                    len(partner_banks) == 1:
                    values.partner_bank_id = partner_banks[0].id

                statement_line_id = statement_line_obj.create(cursor, uid, values)
                results.trans_loaded_cnt += 1
                # Only increase index when all generated transactions are
                # processed as well
                if not injected:
                    i += 1

            results.stat_loaded_cnt += 1
            
        if payment_lines:
            # As payments lines are treated as individual transactions, the
            # batch as a whole is only marked as 'done' when all payment lines
            # have been reconciled.
            cursor.execute(
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
            order_ids = [x[0] for x in cursor.fetchall()]
            if order_ids:
                # Use workflow logics for the orders. Recode logic from
                # account_payment, in order to increase efficiency.
                payment_order_obj.set_done(cursor, uid, order_ids,
                                        {'state': 'done'}
                                       )
                wf_service = netsvc.LocalService('workflow')
                for id in order_ids:
                    wf_service.trg_validate(uid, 'payment.order', id, 'done',
                                            cursor
                                           )

            # Original code. Didn't take workflow logistics into account...
            #
            #cursor.execute(
            #    "UPDATE payment_order o "
            #    "SET state = 'done', "
            #        "date_done = '%s' "
            #    "FROM payment_line l "
            #    "WHERE o.state = 'sent' "
            #      "AND o.id = l.order_id "
            #      "AND l.id NOT IN ("
            #        "SELECT DISTINCT id FROM payment_line "
            #        "WHERE date_done IS NULL "
            #          "AND id IN (%s)"
            #       ")" % (
            #           time.strftime('%Y-%m-%d'),
            #           ','.join([str(x) for x in payment_line_ids])
            #       )
            #)

        report = [
            '%s: %s' % (_('Total number of statements'),
                        results.stat_skipped_cnt + results.stat_loaded_cnt),
            '%s: %s' % (_('Total number of transactions'),
                        results.trans_skipped_cnt + results.trans_loaded_cnt),
            '%s: %s' % (_('Number of errors found'),
                        results.error_cnt),
            '%s: %s' % (_('Number of statements skipped due to errors'),
                        results.stat_skipped_cnt),
            '%s: %s' % (_('Number of transactions skipped due to errors'),
                        results.trans_skipped_cnt),
            '%s: %s' % (_('Number of statements loaded'),
                        results.stat_loaded_cnt),
            '%s: %s' % (_('Number of transactions loaded'),
                        results.trans_loaded_cnt),
            '%s: %s' % (_('Number of transactions matched'),
                        results.trans_matched_cnt),
            '%s: %s' % (_('Number of bank costs invoices created'),
                        results.bank_costs_invoice_cnt),
            '',
            '%s:' % ('Error report'),
            '',
        ]
        text_log = '\n'.join(report + results.log)
        state = results.error_cnt and 'error' or 'ready'
        statement_file_obj.write(cursor, uid, import_id, dict(
            state = state, log = text_log,
            ), context)
        if not imported_statement_ids:
            # file state can be 'ready' while import state is 'error'
            state = 'error'
        self.write(cursor, uid, [ids[0]], dict(
                import_id = import_id, log = text_log, state = state,
                statement_ids = [[6, 0, imported_statement_ids]],
                ), context)
        return {
            'name': _('Import Bank Transactions File'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': self._name,
            'domain': [],
            'context': dict(context, active_ids=ids),
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': ids[0] or False,
        }

    _columns = {
        'company': fields.many2one(
            'res.company', 'Company', required=True,
            states={
                'ready': [('readonly', True)],
                'error': [('readonly', True)],
                },
            ),
        'file': fields.binary(
            'Statements File', required=True,
            help = ('The Transactions File to import. Please note that while it is '
            'perfectly safe to reload the same file multiple times or to load in '
            'timeframe overlapping statements files, there are formats that may '
            'introduce different sequencing, which may create double entries.\n\n'
            'To stay on the safe side, always load bank statements files using the '
            'same format.'),
            states={
                'ready': [('readonly', True)],
                'error': [('readonly', True)],
                },
            ),
        'parser': fields.selection(
            parser_types, 'File Format', required=True,
            states={
                'ready': [('readonly', True)],
                'error': [('readonly', True)],
                },
            ),
        'log': fields.text('Log', readonly=True),
        'state': fields.selection(
            [('init', 'init'), ('ready', 'ready'),
             ('error', 'error')],
            'State', readonly=True),
        'import_id': fields.many2one(
            'account.banking.imported.file', 'Import File'),
        # osv_memory does not seem to support one2many
        'statement_ids': fields.many2many(
            'account.bank.statement', 'rel_wiz_statements', 'wizard_id',
            'statement_id', 'Imported Bank Statements'),
        }

    _defaults = {
        'state': 'init',
        }
banking_import()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
