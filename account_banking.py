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
This module shows resemblance to both account_bankimport/bankimport.py,
account/account_bank_statement.py and account_payment(_export). All hail to
the makers. account_bankimport is only referenced for their ideas and the
framework of the filters, which they in their turn seem to have derived
from account_coda.

Modifications are extensive:

1. In relation to account/account_bank_statement.py:
    account.bank.statement is effectively stripped from its account.period
    association, while account.bank.statement.line is extended with the same
    association, thereby reflecting real world usage of bank.statement as a
    list of bank transactions and bank.statement.line as a bank transaction.

2. In relation to account/account_bankimport:
    All filter objects and extensions to res.company are removed. Instead a
    flexible auto-loading and auto-browsing plugin structure is created,
    whereby business logic and encoding logic are strictly separated.
    Both parsers and business logic are rewritten from scratch.

    The association of account.journal with res.company is replaced by an
    association of account.journal with res.partner.bank, thereby allowing
    multiple bank accounts per company and one journal per bank account.

    The imported bank statement file does not result in a single 'bank
    statement', but in a list of bank statements by definition of whatever the
    bank sees as a statement. Every imported bank statement contains at least
    one bank transaction, which is a modded account.bank.statement.line.

3. In relation to account_payment:
    An additional state was inserted between 'open' and 'done', to reflect a
    exported bank orders file which was not reported back through statements.
    The import of statements matches the payments and reconciles them when
    needed, flagging them 'done'. When no export wizards are found, the
    default behavior is to flag the orders as 'sent', not as 'done'.
'''
import time
from osv import osv, fields
from tools.translate import _

class account_banking_account_settings(osv.osv):
    '''Default Journal for Bank Account'''
    _name = 'account.banking.account.settings'
    _description = __doc__
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', select=True,
                                      required=True),
        'partner_bank_id': fields.many2one('res.partner.bank', 'Bank Account',
                                           select=True, required=True),
        'journal_id': fields.many2one('account.journal', 'Journal',
                                      required=True),
        'default_credit_account_id': fields.many2one(
            'account.account', 'Default credit account', select=True,
            help=('The account to use when an unexpected payment was signaled. '
                  'This can happen when a direct debit payment is cancelled '
                  'by a customer, or when no matching payment can be found. '
                  ' Mind that you can correct movements before confirming them.'
                 ),
            required=True
        ),
        'default_debit_account_id': fields.many2one(
            'account.account', 'Default debit account',
            select=True, required=True,
            help=('The account to use when an unexpected payment is received. '
                  'This can be needed when a customer pays in advance or when '
                  'no matching invoice can be found. Mind that you can correct '
                  'movements before confirming them.'
                 ),
        ),
    }

    def _default_company(self, cursor, uid, context={}):
        user = self.pool.get('res.users').browse(cursor, uid, uid, context=context)
        if user.company_id:
            return user.company_id.id
        return self.pool.get('res.company').search(cursor, uid,
                                                   [('parent_id', '=', False)]
                                                  )[0]

    _defaults = {
        'company_id': _default_company,
    }
account_banking_account_settings()

class account_banking_imported_file(osv.osv):
    '''Imported Bank Statements File'''
    _name = 'account.banking.imported.file'
    _description = __doc__
    _columns = {
        'company_id': fields.many2one('res.company', 'Company',
                                      select=True, readonly=True
                                     ),
        'date': fields.datetime('Import Date', readonly=False, select=True),
        'format': fields.char('File Format', size=20, readonly=False),
        'file': fields.binary('Raw Data', readonly=False),
        'log': fields.text('Import Log', readonly=False),
        'user_id': fields.many2one('res.users', 'Responsible User',
                                   readonly=False, select=True
                                  ),
        'state': fields.selection(
            [('unfinished', 'Unfinished'),
             ('error', 'Error'),
             ('ready', 'Finished'),
            ], 'State', select=True, readonly=True
        ),
        'statement_ids': fields.one2many('account.bank.statement',
                                         'banking_id', 'Statements',
                                         readonly=False,
                                  ),
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda self, cursor, uid, context: uid,
    }
account_banking_imported_file()

class account_bank_statement(osv.osv):
    '''
    Extensions from account_bank_statement:
        1. Removed period_id (transformed to optional boolean) - as it is no
           longer needed.
        2. Extended 'button_confirm' trigger to cope with the period per
           statement_line situation.
        3. Added optional relation with imported statements file
    '''
    _inherit = 'account.bank.statement'
    _columns = {
        'period_id': fields.many2one('account.period', 'Period',
                                     required=False, readonly=True),
        'banking_id': fields.many2one('account.banking.imported.file',
                                     'Imported File', readonly=True,
                                     ),
    }
    _defaults = {
        'period_id': lambda *a: False,
    }

    def _get_period(self, cursor, uid, date, context={}):
        '''
        Find matching period for date, not meant for _defaults.
        '''
        period_obj = self.pool.get('account.period')
        periods = period_obj.find(cursor, uid, dt=date, context=context)
        return periods and periods[0] or False

    def button_confirm(self, cursor, uid, ids, context=None):
        # This is largely a copy of the original code in account
        # As there is no valid inheritance mechanism for large actions, this
        # is the only option to add functionality to existing actions.
        # WARNING: when the original code changes, this trigger has to be
        # updated in sync.
        done = []
        res_currency_obj = self.pool.get('res.currency')
        res_users_obj = self.pool.get('res.users')
        account_move_obj = self.pool.get('account.move')
        account_move_line_obj = self.pool.get('account.move.line')
        account_bank_statement_line_obj = \
                self.pool.get('account.bank.statement.line')

        company_currency_id = res_users_obj.browse(cursor, uid, uid,
                context=context).company_id.currency_id.id

        for st in self.browse(cursor, uid, ids, context):
            if not st.state=='draft':
                continue
            end_bal = st.balance_end or 0.0
            if not (abs(end_bal - st.balance_end_real) < 0.0001):
                raise osv.except_osv(_('Error !'),
                    _('The statement balance is incorrect !\n') +
                    _('The expected balance (%.2f) is different '
                      'than the computed one. (%.2f)') % (
                          st.balance_end_real, st.balance_end
                      ))
            if (not st.journal_id.default_credit_account_id) \
                    or (not st.journal_id.default_debit_account_id):
                raise osv.except_osv(_('Configration Error !'),
                    _('Please verify that an account is defined in the journal.'))

            for line in st.move_line_ids:
                if line.state != 'valid':
                    raise osv.except_osv(_('Error !'),
                        _('The account entries lines are not in valid state.'))

            for move in st.line_ids:
                period_id = self._get_period(cursor, uid, move.date, context=context)
                move_id = account_move_obj.create(cursor, uid, {
                    'journal_id': st.journal_id.id,
                    'period_id': period_id,
                }, context=context)
                account_bank_statement_line_obj.write(cursor, uid, [move.id], {
                    'move_ids': [(4, move_id, False)]
                })
                if not move.amount:
                    continue

                torec = []
                if move.amount >= 0:
                    account_id = st.journal_id.default_credit_account_id.id
                else:
                    account_id = st.journal_id.default_debit_account_id.id
                acc_cur = ((move.amount<=0) and st.journal_id.default_debit_account_id) \
                          or move.account_id
                amount = res_currency_obj.compute(cursor, uid, st.currency.id,
                        company_currency_id, move.amount, context=context,
                        account=acc_cur)
                if move.reconcile_id and move.reconcile_id.line_new_ids:
                    for newline in move.reconcile_id.line_new_ids:
                        amount += newline.amount

                val = {
                    'name': move.name,
                    'date': move.date,
                    'ref': move.ref,
                    'move_id': move_id,
                    'partner_id': ((move.partner_id) and move.partner_id.id) or False,
                    'account_id': (move.account_id) and move.account_id.id,
                    'credit': ((amount>0) and amount) or 0.0,
                    'debit': ((amount<0) and -amount) or 0.0,
                    'statement_id': st.id,
                    'journal_id': st.journal_id.id,
                    'period_id': period_id,
                    'currency_id': st.currency.id,
                }

                amount = res_currency_obj.compute(cursor, uid, st.currency.id,
                        company_currency_id, move.amount, context=context,
                        account=acc_cur)

                if move.account_id and move.account_id.currency_id:
                    val['currency_id'] = move.account_id.currency_id.id
                    if company_currency_id==move.account_id.currency_id.id:
                        amount_cur = move.amount
                    else:
                        amount_cur = res_currency_obj.compute(cursor, uid, company_currency_id,
                                move.account_id.currency_id.id, amount, context=context,
                                account=acc_cur)
                    val['amount_currency'] = amount_cur

                torec.append(account_move_line_obj.create(cursor, uid, val , context=context))

                if move.reconcile_id and move.reconcile_id.line_new_ids:
                    for newline in move.reconcile_id.line_new_ids:
                        account_move_line_obj.create(cursor, uid, {
                            'name': newline.name or move.name,
                            'date': move.date,
                            'ref': move.ref,
                            'move_id': move_id,
                            'partner_id': ((move.partner_id) and move.partner_id.id) or False,
                            'account_id': (newline.account_id) and newline.account_id.id,
                            'debit': newline.amount>0 and newline.amount or 0.0,
                            'credit': newline.amount<0 and -newline.amount or 0.0,
                            'statement_id': st.id,
                            'journal_id': st.journal_id.id,
                            'period_id': period_id,
                        }, context=context)

                # Fill the secondary amount/currency
                # if currency is not the same than the company
                amount_currency = False
                currency_id = False
                if st.currency.id <> company_currency_id:
                    amount_currency = move.amount
                    currency_id = st.currency.id

                account_move_line_obj.create(cursor, uid, {
                    'name': move.name,
                    'date': move.date,
                    'ref': move.ref,
                    'move_id': move_id,
                    'partner_id': ((move.partner_id) and move.partner_id.id) or False,
                    'account_id': account_id,
                    'credit': ((amount < 0) and -amount) or 0.0,
                    'debit': ((amount > 0) and amount) or 0.0,
                    'statement_id': st.id,
                    'journal_id': st.journal_id.id,
                    'period_id': period_id,
                    'amount_currency': amount_currency,
                    'currency_id': currency_id,
                    }, context=context)

                for line in account_move_line_obj.browse(cursor, uid, [x.id for x in 
                        account_move_obj.browse(cursor, uid, move_id, context=context).line_id
                        ], context=context):
                    if line.state != 'valid':
                        raise osv.except_osv(
                            _('Error !'),
                            _('Account move line "%s" is not valid')
                            % line.name
                        )

                if move.reconcile_id and move.reconcile_id.line_ids:
                    torec += map(lambda x: x.id, move.reconcile_id.line_ids)
                    #try:
                    if abs(move.reconcile_amount-move.amount)<0.0001:
                        account_move_line_obj.reconcile(
                            cursor, uid, torec, 'statement', context
                        )
                    else:
                        account_move_line_obj.reconcile_partial(
                            cursor, uid, torec, 'statement', context
                        )
                    #except:
                    #    raise osv.except_osv(
                    #        _('Error !'),
                    #        _('Unable to reconcile entry "%s": %.2f') %
                    #        (move.name, move.amount)
                    #    )

                if st.journal_id.entry_posted:
                    account_move_obj.write(cursor, uid, [move_id], {'state':'posted'})
            done.append(st.id)
        self.write(cursor, uid, done, {'state':'confirm'}, context=context)
        return True

account_bank_statement()

class account_bank_statement_line(osv.osv):
    '''
    Extension on basic class:
        1. Extra links to account.period and res.partner.bank for tracing and
           matching.
        2. Extra 'trans' field to carry the transaction id of the bank.
        3. Extra 'international' flag to indicate the missing of a remote
           account number. Some banks use seperate international banking
           modules that do not integrate with the standard transaction files.
        4. Readonly states for most fields except when in draft.
    '''
    _inherit = 'account.bank.statement.line'
    _description = 'Bank Transaction'

    def _get_period(self, cursor, uid, context={}):
        date = context.get('date') and context['date'] or None
        periods = self.pool.get('account.period').find(cursor, uid, dt=date)
        return periods and periods[0] or False

    def _seems_international(self, cursor, uid, context={}):
        '''
        Some banks have seperate international banking modules which do not
        translate correctly into the national formats. Instead, they
        leave key fields blank and signal this anomaly with a special
        transfer type.
        With the introduction of SEPA, this may worsen greatly, as SEPA
        payments are considered to be analogous to international payments
        by most local formats.
        '''
        # Quick and dirty check: if remote bank account is missing, assume
        # international transfer
        return not (
            context.get('partner_bank_id') and context['partner_bank_id']
        )
        # Not so dirty check: check if partner_id is set. If it is, check the
        # default/invoice addresses country. If it is the same as our
        # company's, its local, else international.
        # TODO: to be done

    _columns = {
        # Redefines
        'amount': fields.float('Amount', readonly=True,
                            states={'draft': [('readonly', False)]}),
        'ref': fields.char('Ref.', size=32, readonly=True,
                            states={'draft': [('readonly', False)]}),
        'name': fields.char('Name', size=64, required=True, readonly=True,
                            states={'draft': [('readonly', False)]}),
        'date': fields.date('Date', required=True, readonly=True,
                            states={'draft': [('readonly', False)]}),
        # New columns
        'trans': fields.char('Bank Transaction ID', size=15, required=False,
                            readonly=True,
                            states={'draft':[('readonly', False)]},
                            ),
        'partner_bank_id': fields.many2one('res.partner.bank', 'Bank Account',
                            required=False, readonly=True,
                            states={'draft':[('readonly', False)]},
                            ),
        'period_id': fields.many2one('account.period', 'Period', required=True,
                            states={'confirm': [('readonly', True)]}),
        # Not used yet, but usefull in the future.
        'international': fields.boolean('International Transaction',
                            required=False,
                            states={'confirm': [('readonly', True)]},
                            ),
    }

    _defaults = {
        'period_id': _get_period,
        'international': _seems_international,
    }

    def onchange_partner_id(self, cursor, uid, line_id, partner_id, type,
                            currency_id, context={}
                           ):
        if not partner_id:
            return {}
        users_obj = self.pool.get('res.users')
        partner_obj = self.pool.get('res.partner')
        
        company_currency_id = users_obj.browse(
                cursor, uid, uid, context=context
            ).company_id.currency_id.id
            
        if not currency_id:
            currency_id = company_currency_id
        
        partner = partner_obj.browse(cursor, uid, partner_id, context=context)
        if partner.supplier and not part.customer:
            account_id = part.property_account_payable.id
            type = 'supplier'
        elif partner.supplier and not part.customer:
            account_id =  part.property_account_receivable.id
            type = 'customer'
        else:
            account_id = 0
            type = 'general'

        return {'value': {'type': type, 'account_id': account_id}}

    def write(self, cursor, uid, ids, values, context={}):
        # TODO: Not sure what to do with this, as it seems that most of
        # this code is related to res_partner_bank and not to this class.
        account_numbers = []
        bank_obj = self.pool.get('res.partner.bank')
        statement_line_obj = self.pool.get('account.bank.statement.line')

        if 'partner_id' in values:
            bank_account_ids = bank_obj.search(cursor, uid,
                                               [('partner_id','=', values['partner_id'])]
                                              )
            bank_accounts = bank_obj.browse(cursor, uid, bank_account_ids)
            import_account_numbers = statement_line_obj.browse(cursor, uid, ids)

            for accno in bank_accounts:
                # Allow acc_number and iban to co-exist (SEPA will unite the
                # two, but - as seen now - in an uneven pace per country)
                if accno.acc_number:
                    account_numbers.append(accno.acc_number)
                if accno.iban:
                    account_numbers.append(accno.iban)

            if any([x for x in import_account_numbers if x.bank_accnumber in
                    account_numbers]):
                for accno in import_account_numbers:
                    account_data = _get_account_data(accno.bank_accnumber)
                    if account_data:
                        bank_id = bank_obj.search(cursor, uid, [
                            ('name', '=', account_data['bank_name'])
                        ])
                        if not bank_id:
                            bank_id = bank_obj.create(cursor, uid, {
                                'name': account_data['bank_name'],
                                'bic': account_data['bic'],
                                'active': 1,
                            })
                        else:
                            bank_id = bank_id[0]

                        bank_acc = bank_obj.create(cursor, uid, {
                            'state': 'bank',
                            'partner_id': values['partner_id'],
                            'bank': bank_id,
                            'acc_number': accno.bank_accnumber,
                        })

                        bank_iban = bank_obj.create(cursor, uid, {
                            'state': 'iban',
                            'partner_id': values['partner_id'],
                            'bank': bank_id,
                            'iban': account_data['iban'],
                        })

                    else:
                        bank_acc = bank_obj.create(cursor, uid, {
                            'state': 'bank',
                            'partner_id': values['partner_id'],
                            'acc_number': accno.bank_accnumber,
                        })

        return super(account_bank_statement_line, self).write(
            cursor, uid, ids, values, context
        )

account_bank_statement_line()

class payment_type(osv.osv):
    '''
    Make description field translatable #, add country context
    '''
    _inherit = 'payment.type'
    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True,
                            help='Payment Type'
                           ),
        #'country_id': fields.many2one('res.country', 'Country',
        #                    required=False,
        #                    help='Use this to limit this type to a specific country'
        #                   ),
    }
    #_defaults = {
    #    'country_id': lambda *a: False,
    #}
payment_type()

class payment_line(osv.osv):
    '''
    Add extra export_state and date_done fields; make destination bank account
    mandatory, as it makes no sense to send payments into thin air.
    '''
    _inherit = 'payment.line'
    _columns = {
        # New fields
        'bank_id': fields.many2one('res.partner.bank',
                                   'Destination Bank account',
                                   required=True
                                  ),
        'export_state': fields.selection([
            ('draft', 'Draft'),
            ('open','Confirmed'),
            ('cancel','Cancelled'),
            ('sent', 'Sent'),
            ('done','Done'),
            ], 'State', select=True
        ),
        # Redefined fields: added states
        'date_done': fields.datetime('Date Confirmed', select=True,
                                     readonly=True),
        'name': fields.char(
            'Your Reference', size=64, required=True,
            states={
                'sent': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'communication': fields.char(
            'Communication', size=64, required=True, 
            help=("Used as the message between ordering customer and current "
                  "company. Depicts 'What do you want to say to the recipient"
                  " about this order ?'"
                 ),
            states={
                'sent': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'communication2': fields.char(
            'Communication 2', size=64,
            help='The successor message of Communication.',
            states={
                'sent': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'move_line_id': fields.many2one(
            'account.move.line', 'Entry line',
            domain=[('reconcile_id','=', False),
                    ('account_id.type', '=','payable')
                   ],
            help=('This Entry Line will be referred for the information of '
                  'the ordering customer.'
                 ),
            states={
                'sent': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'amount_currency': fields.float(
            'Amount in Partner Currency', digits=(16,2),
            required=True,
            help='Payment amount in the partner currency',
            states={
                'sent': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'currency': fields.many2one(
            'res.currency', 'Partner Currency', required=True,
            states={
                'sent': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'bank_id': fields.many2one(
            'res.partner.bank', 'Destination Bank account',
            states={
                'sent': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'order_id': fields.many2one(
            'payment.order', 'Order', required=True,
            ondelete='cascade', select=True,
            states={
                'sent': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'partner_id': fields.many2one(
            'res.partner', string="Partner", required=True,
            help='The Ordering Customer',
            states={
                'sent': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'date': fields.date(
            'Payment Date',
            help=("If no payment date is specified, the bank will treat this "
                  "payment line directly"
                 ),
            states={
                'sent': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'state': fields.selection([
            ('normal','Free'),
            ('structured','Structured')
            ], 'Communication Type', required=True,
            states={
                'sent': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
    }
    _defaults = {
        'export_state': lambda *a: 'draft',
        'date_done': lambda *a: False,
    }
payment_line()

class payment_order(osv.osv):
    '''
    Enable extra state for payment exports
    '''
    _inherit = 'payment.order'
    _columns = {
        'date_planned': fields.date(
            'Scheduled date if fixed',
            states={
                'sent': [('readonly', True)],
                'done': [('readonly', True)]
            },
            help='Select a date if you have chosen Preferred Date to be fixed.'
        ),
        'reference': fields.char(
            'Reference', size=128, required=True,
            states={
                'sent': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'mode': fields.many2one(
            'payment.mode', 'Payment mode', select=True, required=True,
            states={
                'sent': [('readonly', True)],
                'done': [('readonly', True)]
            },
            help='Select the Payment Mode to be applied.'
        ),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('open','Confirmed'),
            ('cancel','Cancelled'),
            ('sent', 'Sent'),
            ('done','Done'),
            ], 'State', select=True
        ),
        'line_ids': fields.one2many(
            'payment.line', 'order_id', 'Payment lines',
            states={
                'sent': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'user_id': fields.many2one(
            'res.users','User', required=True,
            states={
                'sent': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'date_prefered': fields.selection([
            ('now', 'Directly'),
            ('due', 'Due date'),
            ('fixed', 'Fixed date')
            ], "Preferred date", change_default=True, required=True,
            states={
                'sent': [('readonly', True)],
                'done': [('readonly', True)]
            },
            help=("Choose an option for the Payment Order:'Fixed' stands for a "
                  "date specified by you.'Directly' stands for the direct "
                  "execution.'Due date' stands for the scheduled date of "
                  "execution."
                 )
            ),
    }

    def set_to_draft(self, cr, uid, ids, *args):
        cr.execute("UPDATE payment_line "
                   "SET export_state = 'draft' "
                   "WHERE order_id in (%s)" % (
                       ','.join(map(str, ids))
                   ))
        return super(payment_order, self).set_to_draft(
            cr, uid, ids, *args
        )

    def action_sent(self, cr, uid, ids, *args):
        cr.execute("UPDATE payment_line "
                   "SET export_state = 'sent' "
                   "WHERE order_id in (%s)" % (
                       ','.join(map(str, ids))
                   ))
        return True

    def set_done(self, cr, uid, id, *args):
        '''
        Extend standard transition to update childs as well.
        '''
        cr.execute("UPDATE payment_line "
                   "SET export_state = 'done', date_done = '%s' "
                   "WHERE order_id = %s" % (
                       time.strftime('%Y-%m-%d'),
                       self.id
                   ))
        return super(payment_order, self).set_done(
            cr, uid, id, *args
        )

payment_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
