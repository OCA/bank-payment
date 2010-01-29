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
'''
This module contains the business logic of the wizard account_banking_import.
The parsing is done in the parser modules. Every parser module is required to
use parser.models as a mean of communication with the business logic.
'''
import pooler
import time
import wizard
import base64
from tools import config
from tools.translate import _
from account_banking.parsers import models
from account_banking.parsers.convert import *
from banktools import *

def _get_move_info(pool, cursor, uid, move_line):
    reconcile_obj = pool.get('account.bank.statement.reconcile')
    type_map = {
        'out_invoice': 'customer',
        'in_invoice': 'supplier',
        'out_refund': 'customer',
        'in_refund': 'supplier',
    }
    retval = struct(move_line=move_line)
    retval.reference = move_line.ref
    if move_line.invoice:
        retval.invoice = move_line.invoice
        retval.type = type_map[move_line.invoice.type]
    else:
        retval.type = 'general'
    move_line.reconcile_id = reconcile_obj.create(
        cursor, uid, {'line_ids': [(6, 0, [move_line.id])]}
    )
    return retval

def _link_payment(pool, cursor, uid, trans, payment_lines,
                  partner_id, bank_account_id, log):
    '''
    Find the payment order belonging to this reference - if there is one
    This is the easiest part: when sending payments, the returned bank info
    should be identical to ours.
    '''
    # TODO: Not sure what side effects are created when payments are done
    # for credited customer invoices, which will be matched later on too.
    digits = int(config['price_accuracy'])
    candidates = [x for x in payment_lines
                  if x.communication == trans.reference 
                  and round(x.amount, digits) == -round(trans.transferred_amount, digits)
                  and trans.remote_account in (x.bank_id.acc_number,
                                               x.bank_id.iban)
                 ]
    if len(candidates) == 1:
        candidate = candidates[0]
        payment_line_obj = pool.get('payment.line')
        payment_line_obj.write(cursor, uid, [candidate.id], {
            'export_state': 'done',
            'date_done': trans.effective_date.strftime('%Y-%m-%d')}
        )
        
        return _get_move_info(pool, cursor, uid, candidate.move_line_id)

    return False

def _link_invoice(pool, cursor, uid, trans, move_lines,
                  partner_id, bank_account_id, log):
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
        1. Debit amounts are either customer invoices or credited supplier
           invoices.
        2. Credit amounts are either supplier invoices or credited customer
           invoices.
        3. Payments are either below expected amount or only slightly above
           (abs).
        4. Payments from partners that are matched, pay their own invoices.
    
    Worst case scenario:
        1. No match was made.
           No harm done. Proceed with manual matching as usual.
        2. The wrong match was made.
           Statements are encoded in draft. You will have the opportunity to
           manually correct the wrong assumptions. 
    '''
    # First on partner
    candidates = [x for x in move_lines if x.partner_id.id == partner_id]

    # Next on reference/invoice number. Mind that this uses the invoice
    # itself, as the move_line references have been fiddled with on invoice
    # creation. This also enables us to search for the invoice number in the
    # reference instead of the other way around, as most human interventions
    # *add* text.
    if not candidates:
        ref = trans.reference.upper()
        msg = trans.message.upper()
        candidates = [x for x in move_lines 
                      if x.invoice.number.upper() in ref or
                         x.invoice.number.upper() in msg
                     ]

    if len(candidates) > 1:
        # TODO: currency coercing
        digits = int(config['price_accuracy'])
        if trans.transferred_amount < 0:
            func = lambda x, y=abs(trans.transferred_amount), z=digits:\
                    round(x.debit, z) == round(y, z)
        else:
            func = lambda x, y=abs(trans.transferred_amount), z=digits:\
                    round(x.credit, z) == round(y, z)
        best = [x for x in move_lines if func(x)]
        if len(best) != 1:
            log.append(
                _('Unable to link transaction %(trans)s to invoice: '
                  '%(no_candidates)s candidates found; can\'t choose.') % {
                      'trans': trans.id,
                      'no_candidates': len(best)
                  })
            return False

    if len(candidates) == 1:
        return _get_move_info(pool, cursor, uid, candidates[0])

    return False

def _link_canceled_debit(pool, cursor, uid, trans, payment_lines,
                         partner_id, bank_account_id, log):
    '''
    Direct debit transfers can be canceled by the remote owner within a
    legaly defined time period. These 'payments' are most likely
    already marked 'done', which makes them harder to match. Also the
    reconciliation has to be reversed.
    '''
    # TODO: code _link_canceled_debit
    return False

def _banking_import_statements_file(self, cursor, uid, data, context):
    '''
    Import bank statements / bank transactions file.
    This module/function represents the business logic, the parser modules
    represent the decoding logic.
    '''
    form = data['form']
    statements_file = form['file']
    data = base64.decodestring(statements_file)

    pool = pooler.get_pool(cursor.dbname)
    company_obj = pool.get('res.company')
    user_obj = pool.get('res.user')
    journal_obj = pool.get('account.journal')
    move_line_obj = pool.get('account.move.line')
    payment_line_obj = pool.get('payment.line')
    statement_obj = pool.get('account.bank.statement')
    statement_line_obj = pool.get('account.bank.statement.line')
    statement_file_obj = pool.get('account.banking.imported.file')
    #account_obj = pool.get('account.account')
    #payment_order_obj = pool.get('payment.order')
    #currency_obj = pool.get('res.currency')

    # get the parser to parse the file
    parser_code = form['parser']
    parser = models.create_parser(parser_code)
    if not parser:
        raise wizard.except_wizard(
            _('ERROR!'),
            _('Unable to import parser %(parser)s. Parser class not found.') %
            {'parser':parser_code}
        )

    # Get the company
    company = form['company']
    if not company:
        user_data = user_obj.browse(cursor, uid, uid, context)
    company = company_obj.browse(
        cursor, uid, company or user_data.company_id.id, context
    )

    # Parse the file
    statements = parser.parse(data)

    if any([x for x in statements if not x.is_valid()]):
        raise wizard.except_wizard(
            _('ERROR!'),
            _('The imported statements appear to be invalid! Check your file.')
        )

    # Create the file now, as the statements need to be linked to it
    import_id = statement_file_obj.create(cursor, uid, dict(
        company_id = company.id,
        file = statements_file,
        date = time.strftime('%Y-%m-%d'),
        user_id = uid,
        state = 'unfinished'
    ))

    # Results
    no_stat_loaded = 0
    no_trans_loaded = 0
    no_stat_skipped = 0
    no_trans_skipped = 0
    no_trans_matched = 0
    no_errors = 0
    log = []

    # Caching
    error_accounts = {}
    info = {}
    imported_statement_ids = []

    if statements:
        # Get interesting journals once
        if company:
            journal_ids = journal_obj.search(cursor, uid, [
                ('type', 'in', ('sale','purchase')),
                ('company_id', '=', company.id),
            ])
        else:
            journal_ids = None
        if not journal_ids:
            journal_ids = journal_obj.search(cursor, uid, [
                ('type', 'in', ('sale','purchase')),
                ('active', '=', True),
                ('company_id', '=', False),
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
        move_lines = move_line_obj.browse(cursor, uid, move_line_ids)

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
            no_stat_skipped += 1
            no_trans_skipped += len(statement.transactions)
            continue

        if not statement.local_account in info:
            account_info = get_company_bank_account(
                pool, cursor, uid, statement.local_account, company, log
            )
            if not account_info:
                log.append(
                    _('Statements found for unknown account %(bank_account)s') %
                    {'bank_account': statement.local_account}
                )
                error_accounts[statement.local_account] = True
                no_errors += 1
                continue
            if 'journal_id' not in account_info:
                log.append(
                    _('Statements found for account %(bank_account)s, '
                      'but no default journal was defined.'
                     ) % {'bank_account': statement.local_account}
                )
                error_accounts[statement.local_account] = True
                no_errors += 1
                continue
            info[statement.local_account] = account_info
        else:
            account_info = info[statement.local_account]

        if statement.local_currency \
           and account_info.journal_id.code != statement.local_currency:
            # TODO: convert currencies?
            log.append(
                _('Statement for account %(bank_account)s uses different '
                  'currency than the defined bank journal.') %
                  {'bank_account': statement.local_account}
            )
            error_accounts[statement.local_account] = True
            no_errors += 1
            continue

        # Check existence of previous statement
        statement_ids = statement_obj.search(cursor, uid, [
            ('name', '=', statement.id),
            ('date', '=', date2str(statement.date)),
        ])
        if statement_ids:
            log.append(
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
            currency = account_info.journal_id.currency.id,
            user_id = uid,
            banking_id = import_id,
        ))
        imported_statement_ids.append(statement_id)

        # move each line to the right period and try to match it with an
        # invoice or payment
        subno = 0
        for transaction in statement.transactions:
            move_info = False

            # Keep a tracer for identification of order in a statement in case
            # of missing transaction ids.
            subno += 1

            # Link remote partner, import account when needed
            partner_bank = get_bank_account(
                pool, cursor, uid, transaction.remote_account, log, fail=True
            )
            if partner_bank:
                partner_id = partner_bank.partner_id.id
                partner_bank_id = partner_bank.id
            elif transaction.remote_owner:
                partner_id = get_or_create_partner(
                    pool, cursor, uid, transaction.remote_owner
                )
                if transaction.remote_account:
                    partner_bank_id = create_bank_account(
                        pool, cursor, uid, partner_id,
                        transaction.remote_account, transaction.remote_owner,
                        log
                    )
            else:
                partner_id = False
                partner_bank_id = False

            # Link accounting period
            period_id = get_period(pool, cursor, uid,
                                   transaction.effective_date, company,
                                   log)
            if not period_id:
                no_trans_skipped += 1
                continue

            # Credit means payment... isn't it?
            if transaction.transferred_amount < 0 and payment_lines:
                # Link open payment - if any
                move_info = _link_payment(pool, cursor, uid, transaction,
                                          payment_lines, partner_id,
                                          partner_bank_id, log
                                         )

            # Second guess, invoice
            if not move_info:
                # Link invoice - if any
                move_info = _link_invoice(pool, cursor, uid, transaction,
                                          move_lines, partner_id, partner_bank_id,
                                          log
                                         )
            if not move_info:
                if transaction.transferred_amount < 0:
                    account_id = account_info.default_credit_account_id
                else:
                    account_id = account_info.default_debit_account_id
            else:
                account_id = move_info.move_line.account_id
                no_trans_matched += 1

            values = struct(
                name = '%s.%s' % (statement.id, transaction.id or subno),
                date = transaction.effective_date,
                amount = transaction.transferred_amount,
                account_id = account_id.id,
                statement_id = statement_id,
                note = transaction.message,
                ref = transaction.reference,
                period_id = period_id,
            )
            if partner_id:
                values.partner_id = partner_id
            if partner_bank_id:
                values.partner_bank_id = partner_bank_id
            if move_info:
                values.type = move_info.type
                values.reconcile_id = move_info.move_line.reconcile_id

            statement_line_id = statement_line_obj.create(cursor, uid, values)
            no_trans_loaded += 1

        no_stat_loaded += 1

    if payment_lines:
        # As payments lines are treated as individual transactions, the
        # batch as a whole is only marked as 'done' when all payment lines
        # have been reconciled.
        cursor.execute(
            "UPDATE payment_order o "
            "SET state = 'done', "
                "date_done = '%s' "
            "FROM payment_line l "
            "WHERE o.state = 'sent' "
              "AND o.id = l.order_id "
              "AND o.id NOT IN ("
                "SELECT DISTINCT id FROM payment_line "
                "WHERE date_done IS NULL "
                  "AND id IN (%s)"
               ")" % (
                   time.strftime('%Y-%m-%d'),
                   ','.join([str(x) for x in payment_line_ids])
               )
        )
    report = [
        '%s: %s' % (_('Total number of statements'), no_stat_skipped + no_stat_loaded),
        '%s: %s' % (_('Total number of transactions'), no_trans_skipped + no_trans_loaded),
        '%s: %s' % (_('Number of errors found'), no_errors),
        '%s: %s' % (_('Number of statements skipped due to errors'), no_stat_skipped),
        '%s: %s' % (_('Number of transactions skipped due to errors'), no_trans_skipped),
        '%s: %s' % (_('Number of statements loaded'), no_stat_loaded),
        '%s: %s' % (_('Number of transactions loaded'), no_trans_loaded),
        '',
        '%s:' % ('Error report'),
        '',
    ]
    text_log = '\n'.join(report + log)
    state = no_errors and 'error' or 'ready'
    statement_file_obj.write(cursor, uid, import_id, dict(
        state = state, log = text_log,
    ))
    return dict(
        log = text_log,
        statement_ids = imported_statement_ids
    )

banking_import_form = '''<?xml version="1.0"?>
<form string="Import Bank Transactions File">
<separator colspan="4" string="Select the processing details:" />
    <field name="company" colspan="1" />
    <field name="file"/>
    <newline />
    <field name="parser"/>
</form>
'''

def parser_types(*args, **kwargs):
    '''Delay evaluation of parser types until start of wizard, to allow
       depending modules to initialize and add their parsers to the list
    '''
    return models.parser_type.get_parser_types()

banking_import_fields = dict(
    company = dict(
        string = 'Company',
        type = 'many2one',
        relation = 'res.company',
        required = True,
    ),
    file = dict(
        string = 'Statements File',
        type = 'binary',
        required = True,
        help = ('The Transactions File to import. Please note that while it is '
        'perfectly safe to reload the same file multiple times or to load in '
        'timeframe overlapping statements files, there are formats that may '
        'introduce different sequencing, which may create double entries.\n\n'
        'To stay on the safe side, always load bank statements files using the '
        'same format.')
    ),
    parser = dict(
        string = 'File Format',
        type = 'selection',
        selection = parser_types,
        required = True,
    ),
)

result_form = '''<?xml version="1.0"?>
<form string="Import Bank Transactions File">
    <separator colspan="4" string="Results:" />
    <field name="log" colspan="4" nolabel="1" width="500"/>
</form>
'''

result_fields = dict(
    log = dict(string='Log', type='text')
)

class banking_import(wizard.interface):
    '''
    Wizard to import bank statements. Generic code, parsing is done in the
    parser modules.
    '''

    def _action_open_window(self, cursor, uid, data, context):
        '''
        Open a window with the resulting bank statements
        '''
        # TODO: this needs fiddling. The resulting window is informative,
        # but not very usefull...
        form = data['form']
        return dict(
            domain = "[('id','in',(%s,))]" % (','.join(map(str, form['statement_ids']))),
            name = 'Statement',
            view_type = 'tree',
            view_mode = 'form,tree',
            res_model = 'account.bank.statement',
            view_id = False,
            type = 'ir.actions.act_window',
            res_id = form['statement_ids'],
        )

    states = {
        'init' : {
            'actions' : [],
            'result' : {
                'type' : 'form',
                'arch' : banking_import_form,
                'fields': banking_import_fields,
                'state': [('end', '_Cancel', 'gtk-cancel'),
                          ('import', '_Ok', 'gtk-ok'),
                         ]
            }
         },
         'import' : {
            'actions': [_banking_import_statements_file],
            'result': {
                'type': 'form',
                'arch': result_form,
                'fields': result_fields,
                'state': [('end', '_Close', 'gtk-close'),
                          ('open', '_Open Statement', 'gtk-ok'),
                         ]
            }
        },
        'open': {
            'actions': [],
            'result': {
                'type': 'action',
                'action': _action_open_window,
                'state': 'end'
            }
        },
    }

banking_import('account_banking.banking_import')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
