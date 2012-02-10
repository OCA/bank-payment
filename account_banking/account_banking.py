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
    Rejected payments from the bank receive on import the status 'rejected'.
'''
import time
import sys
import sepa
from osv import osv, fields
from tools.translate import _
from wizard.banktools import get_or_create_bank
import decimal_precision as dp
import pooler
import netsvc

def warning(title, message):
    '''Convenience routine'''
    return {'warning': {'title': title, 'message': message}}

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
        'costs_account_id': fields.many2one(
            'account.account', 'Bank Costs Account', select=True,
            help=('The account to use when the bank invoices its own costs. '
                  'Leave it blank to disable automatic invoice generation '
                  'on bank costs.'
                 ),
        ),
        'invoice_journal_id': fields.many2one(
            'account.journal', 'Costs Journal', 
            help=('This is the journal used to create invoices for bank costs.'
                 ),
        ),
        'bank_partner_id': fields.many2one(
            'res.partner', 'Bank Partner',
            help=('The partner to use for bank costs. Banks are not partners '
                  'by default. You will most likely have to create one.'
                 ),
        ),

        #'multi_currency': fields.boolean(
        #    'Multi Currency Bank Account', required=True,
        #    help=('Select this if your bank account is able to handle '
        #          'multiple currencies in parallel without coercing to '
        #          'a single currency.'
        #         ),
        #),
    }

    def _default_company(self, cursor, uid, context=None):
        user = self.pool.get('res.users').browse(cursor, uid, uid, context=context)
        if user.company_id:
            return user.company_id.id
        return self.pool.get('res.company').search(cursor, uid,
                                                   [('parent_id', '=', False)]
                                                  )[0]

    _defaults = {
        'company_id': _default_company,
        #'multi_currency': lambda *a: False,
    }
account_banking_account_settings()

class account_banking_imported_file(osv.osv):
    '''Imported Bank Statements File'''
    _name = 'account.banking.imported.file'
    _description = __doc__
    _rec_name = 'date'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company',
                                      select=True, readonly=True
                                     ),
        'date': fields.datetime('Import Date', readonly=True, select=True,
                                states={'draft': [('unfinished', False)]}
                               ),
        'format': fields.char('File Format', size=20, readonly=True,
                              states={'draft': [('unfinished', False)]}
                             ),
        'file': fields.binary('Raw Data', readonly=True,
                              states={'draft': [('unfinished', False)]}
                             ),
        'log': fields.text('Import Log', readonly=True,
                           states={'draft': [('unfinished', False)]}
                          ),
        'user_id': fields.many2one('res.users', 'Responsible User',
                                   readonly=True, select=True,
                                   states={'draft': [('unfinished', False)]}
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

class payment_mode_type(osv.osv):
    _name= 'payment.mode.type'
    _description= 'Payment Mode Type'
    _columns= {
        'name': fields.char(
            'Name', size=64, required=True,
            help='Payment Type'
            ),
        'code': fields.char(
            'Code', size=64, required=True,
            help='Specify the Code for Payment Type'
            ),
        # Setting suitable_bank_types to required pending
        # https://bugs.launchpad.net/openobject-addons/+bug/786845
        'suitable_bank_types': fields.many2many(
            'res.partner.bank.type',
            'bank_type_payment_type_rel',
            'pay_type_id','bank_type_id',
            'Suitable bank types', required=True),
        'ir_model_id': fields.many2one(
            'ir.model', 'Payment wizard',
            help=('Select the Payment Wizard for payments of this type. '
                  'Leave empty for manual processing'),
            domain=[('osv_memory', '=', True)],
            ),
    }

payment_mode_type()

class payment_mode(osv.osv):
    ''' Restoring the payment type from version 5,
    used to select the export wizard (if any) '''
    _inherit = "payment.mode"

    def suitable_bank_types(self, cr, uid, payment_mode_id=None, context=None):
        """ Reinstates functional code for suitable bank type filtering.
        Current code in account_payment is disfunctional.
        """
        res = []
        payment_mode = self.browse(
            cr, uid, payment_mode_id, context)
        if (payment_mode and payment_mode.type and
            payment_mode.type.suitable_bank_types):
            res = [type.code for type in payment_mode.type.suitable_bank_types]
        return res

    _columns = {
        'type': fields.many2one(
            'payment.mode.type', 'Payment type',
            help='Select the Payment Type for the Payment Mode.'
            ),
        }
payment_mode()

class account_bank_statement(osv.osv):
    '''
    Extensions from account_bank_statement:
        1. Removed period_id (transformed to optional boolean) - as it is no
           longer needed.
           NB! because of #1. changes required to account_voucher!
        2. Extended 'button_confirm' trigger to cope with the period per
           statement_line situation.
        3. Added optional relation with imported statements file
        4. Ordering is based on auto generated id.
    '''
    _inherit = 'account.bank.statement'
    _order = 'id'
    _abf_others = []
    _abf_others_loaded = False

    def __init__(self, *args, **kwargs):
        '''
        See where we stand in the order of things
        '''
        super(account_bank_statement, self).__init__(*args, **kwargs)
        if not self._abf_others_loaded:
            self._abf_others_loaded = True
            self._abf_others = [x for x in self.__class__.__mro__
                                   if x.__module__.split('.')[0] not in [
                                       'osv', 'account', 'account_banking',
                                       '__builtin__'
                                   ]
                               ]

    #def _currency(self, cursor, user, ids, name, args, context=None):
    #    '''
    #    Calculate currency from contained transactions
    #    '''
    #    res = {}
    #    res_currency_obj = self.pool.get('res.currency')
    #    res_users_obj = self.pool.get('res.users')
    #    default_currency = res_users_obj.browse(cursor, user,
    #            user, context=context).company_id.currency_id
    #    for statement in self.browse(cursor, user, ids, context=context):
    #        currency = statement.journal_id.currency
    #        if not currency:
    #            currency = default_currency
    #        res[statement.id] = currency.id
    #    currency_names = {}
    #    for currency_id, currency_name in res_currency_obj.name_get(cursor,
    #            user, res.values(), context=context):
    #        currency_names[currency_id] = currency_name
    #    for statement_id in res.keys():
    #        currency_id = res[statement_id]
    #        res[statement_id] = (currency_id, currency_names[currency_id])
    #    return res

    _columns = {
        'period_id': fields.many2one('account.period', 'Period',
                                     required=False, readonly=True),
        'banking_id': fields.many2one('account.banking.imported.file',
                                     'Imported File', readonly=True,
                                     ),
    #    'currency': fields.function(_currency, method=True, string='Currency',
    #        type='many2one', relation='res.currency'),
    }

    _defaults = {
        'period_id': lambda *a: False,
    #    'currency': _currency,
    }

    def _get_period(self, cursor, uid, date, context=None):
        '''
        Find matching period for date, not meant for _defaults.
        '''
        period_obj = self.pool.get('account.period')
        periods = period_obj.find(cursor, uid, dt=date, context=context)
        return periods and periods[0] or False

    #def compute(self, cursor, uid, ids, context=None):
    #    '''
    #    Compute start and end balance with mixed currencies.
    #    '''
    #    return None

    def create_move_from_st_line(self, cr, uid, st_line_id,
                                 company_currency_id, st_line_number,
                                 context=None):
        # This is largely a copy of the original code in account
        # Modifications are marked with AB
        # As there is no valid inheritance mechanism for large actions, this
        # is the only option to add functionality to existing actions.
        # WARNING: when the original code changes, this trigger has to be
        # updated in sync.
        if context is None:
            context = {}
        res_currency_obj = self.pool.get('res.currency')
        account_move_obj = self.pool.get('account.move')
        account_move_line_obj = self.pool.get('account.move.line')
        account_bank_statement_line_obj = self.pool.get(
            'account.bank.statement.line')
        st_line = account_bank_statement_line_obj.browse(cr, uid, st_line_id,
                                                         context=context)
        st = st_line.statement_id

        context.update({'date': st_line.date})
        period_id = self._get_period(
            cr, uid, st_line.date, context=context) # AB

        move_id = account_move_obj.create(cr, uid, {
            'journal_id': st.journal_id.id,
            'period_id': period_id, # AB
            'date': st_line.date,
            'name': st_line_number,
        }, context=context)
        account_bank_statement_line_obj.write(cr, uid, [st_line.id], {
            'move_ids': [(4, move_id, False)]
        })

        if st_line.amount >= 0:
            account_id = st.journal_id.default_credit_account_id.id
        else:
            account_id = st.journal_id.default_debit_account_id.id

        acc_cur = ((st_line.amount <= 0 and
                    st.journal_id.default_debit_account_id) or
                   st_line.account_id)
        context.update({
                'res.currency.compute.account': acc_cur,
            })
        amount = res_currency_obj.compute(cr, uid, st.currency.id,
                company_currency_id, st_line.amount, context=context)

        val = {
            'name': st_line.name,
            'date': st_line.date,
            'ref': st_line.ref,
            'move_id': move_id,
            'partner_id': (((st_line.partner_id) and st_line.partner_id.id) or
                           False),
            'account_id': (st_line.account_id) and st_line.account_id.id,
            'credit': ((amount>0) and amount) or 0.0,
            'debit': ((amount<0) and -amount) or 0.0,
            'statement_id': st.id,
            'journal_id': st.journal_id.id,
            'period_id': period_id, # AB
            'currency_id': st.currency.id,
            'analytic_account_id': (st_line.analytic_account_id and
                                    st_line.analytic_account_id.id or
                                    False),
        }

        if st.currency.id <> company_currency_id:
            amount_cur = res_currency_obj.compute(cr, uid, company_currency_id,
                        st.currency.id, amount, context=context)
            val['amount_currency'] = -amount_cur

        if (st_line.account_id and st_line.account_id.currency_id and
            st_line.account_id.currency_id.id <> company_currency_id):
            val['currency_id'] = st_line.account_id.currency_id.id
            amount_cur = res_currency_obj.compute(cr, uid, company_currency_id,
                    st_line.account_id.currency_id.id, amount, context=context)
            val['amount_currency'] = -amount_cur

        move_line_id = account_move_line_obj.create(
            cr, uid, val, context=context)
        torec = move_line_id

        # Fill the secondary amount/currency
        # if currency is not the same than the company
        amount_currency = False
        currency_id = False
        if st.currency.id <> company_currency_id:
            amount_currency = st_line.amount
            currency_id = st.currency.id
        account_move_line_obj.create(cr, uid, {
            'name': st_line.name,
            'date': st_line.date,
            'ref': st_line.ref,
            'move_id': move_id,
            'partner_id': (((st_line.partner_id) and st_line.partner_id.id) or
                           False),
            'account_id': account_id,
            'credit': ((amount < 0) and -amount) or 0.0,
            'debit': ((amount > 0) and amount) or 0.0,
            'statement_id': st.id,
            'journal_id': st.journal_id.id,
            'period_id': period_id, # AB
            'amount_currency': amount_currency,
            'currency_id': currency_id,
            }, context=context)

        for line in account_move_line_obj.browse(cr, uid, [x.id for x in
                account_move_obj.browse(cr, uid, move_id,
                    context=context).line_id],
                context=context):
            if line.state <> 'valid':
                raise osv.except_osv(_('Error !'),
                        _('Journal Item "%s" is not valid') % line.name)

        # Bank statements will not consider boolean on journal entry_posted
        account_move_obj.post(cr, uid, [move_id], context=context)
        
        """ 
        Account-banking:
        - Write stored reconcile_id
        - Pay invoices through workflow 
        """
        if st_line.reconcile_id:
            account_move_line_obj.write(cr, uid, [torec], {
                    'reconcile_id': st_line.reconcile_id.id }, context=context)
            for move_line in (st_line.reconcile_id.line_id or []) + (
                st_line.reconcile_id.line_partial_ids or []):
                netsvc.LocalService("workflow").trg_trigger(
                    uid, 'account.move.line', move_line.id, cr)
        """ End account-banking """

        return move_id

    def button_confirm_bank(self, cr, uid, ids, context=None):
        if context is None: context = {}
        obj_seq = self.pool.get('ir.sequence')
        if not isinstance(ids, list): ids = [ids]
        noname_ids = self.search(cr, uid, [('id','in',ids),('name','=','/')])
        for st in self.browse(cr, uid, noname_ids, context=context):
                if st.journal_id.sequence_id:
                    year = self.pool.get('account.period').browse(cr, uid, self._get_period(cr, uid, st.date)).fiscalyear_id.id
                    c = {'fiscalyear_id': year}
                    st_number = obj_seq.get_id(cr, uid, st.journal_id.sequence_id.id, context=c)
                    self.write(cr, uid, ids, {'name': st_number})
        
        return super(account_bank_statement, self).button_confirm_bank(cr, uid, ids, context)

account_bank_statement()

class account_voucher(osv.osv):
    _inherit = 'account.voucher'

    def _get_period(self, cr, uid, context=None):
        if context is None: context = {}
        if not context.get('period_id') and context.get('move_line_ids'):
            res = self.pool.get('account.move.line').browse(cr, uid , context.get('move_line_ids'))[0].period_id.id
            context['period_id'] = res
        return super(account_voucher, self)._get_period(cr, uid, context)

    def create(self, cr, uid, values, context=None):
        if values.get('period_id') == False and context.get('move_line_ids'):
            values['period_id'] = self._get_period(cr, uid, context)
        return super(account_voucher, self).create(cr, uid, values, context)

account_voucher()

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

    def _get_period(self, cursor, user, context=None):
        date = context.get('date', None)
        periods = self.pool.get('account.period').find(cursor, user, dt=date)
        return periods and periods[0] or False

    def _seems_international(self, cursor, user, context=None):
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

    def _get_currency(self, cursor, user, context=None):
        '''
        Get the default currency (required to allow other modules to function,
        which assume currency to be a calculated field and thus optional)
        Remark: this is only a fallback as the real default is in the journal,
        which is inaccessible from within this method.
        '''
        res_users_obj = self.pool.get('res.users')
        return res_users_obj.browse(cursor, user, user,
                context=context).company_id.currency_id.id

    #def _reconcile_amount(self, cursor, user, ids, name, args, context=None):
    #    '''
    #    Redefinition from the original: don't use the statements currency, but
    #    the transactions currency.
    #    '''
    #    if not ids:
    #        return {}

    #    res_currency_obj = self.pool.get('res.currency')
    #    res_users_obj = self.pool.get('res.users')

    #    res = {}
    #    company_currency_id = res_users_obj.browse(cursor, user, user,
    #            context=context).company_id.currency_id.id

    #    for line in self.browse(cursor, user, ids, context=context):
    #        if line.reconcile_id:
    #            res[line.id] = res_currency_obj.compute(cursor, user,
    #                    company_currency_id, line.currency.id,
    #                    line.reconcile_id.total_entry, context=context)
    #        else:
    #            res[line.id] = 0.0
    #    return res

    def _get_invoice_id(self, cr, uid, ids, name, args, context=None):
        res = {}
        for st_line in self.browse(cr, uid, ids, context):
            res[st_line.id] = False
            for move_line in (st_line.reconcile_id and
                              (st_line.reconcile_id.line_id or []) +
                              (st_line.reconcile_id.line_partial_ids or []) or
                              []):
                if move_line.invoice:
                    res[st_line.id] = move_line.invoice.id
                    continue
        return res

    _columns = {
        # Redefines
        'amount': fields.float('Amount', readonly=True,
                            digits_compute=dp.get_precision('Account'),
                            states={'draft': [('readonly', False)]}),
        'ref': fields.char('Ref.', size=32, readonly=True,
                            states={'draft': [('readonly', False)]}),
        'name': fields.char('Name', size=64, required=False, readonly=True,
                            states={'draft': [('readonly', False)]}),
        'date': fields.date('Date', required=True, readonly=True,
                            states={'draft': [('readonly', False)]}),
        #'reconcile_amount': fields.function(_reconcile_amount,
        #    string='Amount reconciled', method=True, type='float'),

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
        'currency': fields.many2one('res.currency', 'Currency', required=True,
                            states={'confirm': [('readonly', True)]}),

        # Not used yet, but usefull in the future.
        'international': fields.boolean('International Transaction',
                            required=False,
                            states={'confirm': [('readonly', True)]},
                            ),
        'reconcile_id': fields.many2one(
            'account.move.reconcile', 'Reconciliation', readonly=True
            ),
        'invoice_id': fields.function(
            _get_invoice_id, method=True, string='Linked Invoice',
            type='many2one', relation='account.invoice'
            ),
    }

    _defaults = {
        'period_id': _get_period,
        'international': _seems_international,
        'currency': _get_currency,
    }

account_bank_statement_line()

class payment_line(osv.osv):
    '''
    Add extra export_state and date_done fields; make destination bank account
    mandatory, as it makes no sense to send payments into thin air.
    Edit: Payments can be by cash too, which is prohibited by mandatory bank
    accounts.
    '''
    _inherit = 'payment.line'
    _columns = {
        # New fields
        'export_state': fields.selection([
            ('draft', 'Draft'),
            ('open','Confirmed'),
            ('cancel','Cancelled'),
            ('sent', 'Sent'),
            ('rejected', 'Rejected'),
            ('done','Done'),
            ], 'State', select=True
        ),
        'msg': fields.char('Message', size=255, required=False, readonly=True),

        # Redefined fields: added states
        'date_done': fields.datetime('Date Confirmed', select=True,
                                     readonly=True),
        'name': fields.char(
            'Your Reference', size=64, required=True,
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'communication': fields.char(
            'Communication', size=64, required=False, 
            help=("Used as the message between ordering customer and current "
                  "company. Depicts 'What do you want to say to the recipient"
                  " about this order ?'"
                 ),
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'communication2': fields.char(
            'Communication 2', size=128,
            help='The successor message of Communication.',
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
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
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'amount_currency': fields.float(
            'Amount in Partner Currency', digits=(16,2),
            required=True,
            help='Payment amount in the partner currency',
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'currency': fields.many2one(
            'res.currency', 'Partner Currency', required=True,
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'bank_id': fields.many2one(
            'res.partner.bank', 'Destination Bank account',
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'order_id': fields.many2one(
            'payment.order', 'Order', required=True,
            ondelete='cascade', select=True,
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'partner_id': fields.many2one(
            'res.partner', string="Partner", required=True,
            help='The Ordering Customer',
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
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
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'state': fields.selection([
            ('normal','Free'),
            ('structured','Structured')
            ], 'Communication Type', required=True,
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
    }
    _defaults = {
        'export_state': lambda *a: 'draft',
        'date_done': lambda *a: False,
        'msg': lambda *a: '',
    }

    def fields_get(self, cr, uid, fields=None, context=None):
        res = super(payment_line, self).fields_get(cr, uid, fields, context)
        if 'communication' in res:
            res['communication'].setdefault('states', {})
            res['communication']['states']['structured'] = [('required', True)]
        if 'communication2' in res:
            res['communication2'].setdefault('states', {})
            res['communication2']['states']['structured'] = [('readonly', True)]
            res['communication2']['states']['normal'] = [('readonly', False)]

        return res


payment_line()

class payment_order(osv.osv):
    '''
    Enable extra states for payment exports
    '''
    _inherit = 'payment.order'

    _columns = {
        'date_scheduled': fields.date(
            'Scheduled date if fixed',
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
            help='Select a date if you have chosen Preferred Date to be fixed.'
        ),
        'reference': fields.char(
            'Reference', size=128, required=True,
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'mode': fields.many2one(
            'payment.mode', 'Payment mode', select=True, required=True,
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
            help='Select the Payment Mode to be applied.'
        ),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('open','Confirmed'),
            ('cancel','Cancelled'),
            ('sent', 'Sent'),
            ('rejected', 'Rejected'),
            ('done','Done'),
            ], 'State', select=True
        ),
        'line_ids': fields.one2many(
            'payment.line', 'order_id', 'Payment lines',
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'user_id': fields.many2one(
            'res.users','User', required=True,
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
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
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
            help=("Choose an option for the Payment Order:'Fixed' stands for a "
                  "date specified by you.'Directly' stands for the direct "
                  "execution.'Due date' stands for the scheduled date of "
                  "execution."
                 )
            ),
    }

    def launch_wizard(self, cr, uid, ids, context=None):
        """
        Search for a wizard to launch according to the type.
        If type is manual. just confirm the order.
        Previously (pre-v6) in account_payment/wizard/wizard_pay.py
        """
        if context == None:
            context={}
        result = {}
        orders = self.browse(cr, uid, ids, context)
        order = orders[0]
        # check if a wizard is defined for the first order
        if order.mode.type and order.mode.type.ir_model_id:
            context['active_ids'] = ids
            wizard_model = order.mode.type.ir_model_id.model
            wizard_obj = self.pool.get(wizard_model)
            wizard_id = wizard_obj.create(cr, uid, {}, context)
            result = {
                'name': wizard_obj._description or 'Payment Order Export',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': wizard_model,
                'domain': [],
                'context': context,
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': wizard_id,
                'nodestroy': True,
                }
        else:
            # should all be manual orders without type or wizard model
            for order in orders[1:]:
                if order.mode.type and order.mode.type.ir_model_id:
                    raise osv.except_osv(
                        _('Error'),
                        _('You can only combine payment orders of the same type')
                        )
            # process manual payments
            self.action_sent(cr, uid, ids, context)
        return result

    def _write_payment_lines(self, cursor, uid, ids, **kwargs):
        '''
        ORM method for setting attributes of corresponding payment.line objects.
        Note that while this is ORM compliant, it is also very ineffecient due
        to the absence of filters on writes and hence the requirement to
        filter on the client(=OpenERP server) side.
        '''
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        payment_line_obj = self.pool.get('payment.line')
        line_ids = payment_line_obj.search(
            cursor, uid, [
                ('order_id', 'in', ids)
            ])
        payment_line_obj.write(cursor, uid, line_ids, kwargs)

    def set_to_draft(self, cursor, uid, ids, *args):
        '''
        Set both self and payment lines to state 'draft'.
        '''
        self._write_payment_lines(cursor, uid, ids, export_state='draft')
        return super(payment_order, self).set_to_draft(
            cursor, uid, ids, *args
        )

    def action_sent(self, cursor, uid, ids, *args):
        '''
        Set both self and payment lines to state 'sent'.
        '''
        self._write_payment_lines(cursor, uid, ids, export_state='sent')
        wf_service = netsvc.LocalService('workflow')
        for id in ids:
            wf_service.trg_validate(uid, 'payment.order', id, 'sent', cursor)
        return True

    def action_rejected(self, cursor, uid, ids, *args):
        '''
        Set both self and payment lines to state 'rejected'.
        '''
        self._write_payment_lines(cursor, uid, ids, export_state='rejected')
        wf_service = netsvc.LocalService('workflow')
        for id in ids:
            wf_service.trg_validate(uid, 'payment.order', id, 'rejected', cursor)
        return True

    def set_done(self, cursor, uid, ids, *args):
        '''
        Extend standard transition to update children as well.
        '''
        self._write_payment_lines(cursor, uid, ids,
                                  export_state='done',
                                  date_done=time.strftime('%Y-%m-%d')
                                 )
        return super(payment_order, self).set_done(
            cursor, uid, ids, *args
        )

    def get_wizard(self, type):
        '''
        Intercept manual bank payments to include 'sent' state. Default
        'manual' payments are flagged 'done' immediately.
        '''
        if type == 'BANKMAN':
            # Note that self._module gets overwritten by inheriters, so make
            # the module name hard coded.
            return 'account_banking', 'wizard_account_banking_payment_manual'
        return super(payment_order, self).get_wizard(type)

payment_order()

class res_partner_bank(osv.osv):
    '''
    This is a hack to circumvent the very limited but widely used base_iban
    dependency. The usage of __mro__ requires inside information of
    inheritence. This code is tested and works - it bypasses base_iban
    altogether. Be sure to use 'super' for inherited classes from here though.

    Extended functionality:
        1. BBAN and IBAN are considered equal
        2. Online databases are checked when available
        3. Banks are created on the fly when using IBAN
        4. Storage is uppercase, not lowercase
        5. Presentation is formal IBAN
        6. BBAN's are generated from IBAN when possible
        7. In the absence of online databanks, BBAN's are checked on format
           using IBAN specs.
    '''
    _inherit = 'res.partner.bank'
    _columns = {
        'iban': fields.char('IBAN', size=34,
                            help="International Bank Account Number"
                           ),
    }

    def __init__(self, *args, **kwargs):
        '''
        Locate founder (first non inherited class) in inheritance tree.
        Defaults to super()
        Algorithm should prevent moving unknown classes between
        base.res_partner_bank and this module's res_partner_bank.
        '''
        self._founder = super(res_partner_bank, self)
        self._founder.__init__(*args, **kwargs)
        mro = self.__class__.__mro__
        for i in range(len(mro)):
            if mro[i].__module__.startswith('base.'):
                self._founder = mro[i]
                break

    def init(self, cursor):
        '''
        Update existing iban accounts to comply to new regime
        Note that usage of the ORM is not possible here, as the ORM cannot
        search on values not provided by the client.
        '''
        cursor.execute('SELECT id, acc_number, iban '
                       'FROM res_partner_bank '
                       'WHERE '
                         'upper(iban) != iban OR '
                         'acc_number IS NULL'
                      )
        for id, acc_number, iban in cursor.fetchall():
            new_iban = new_acc_number = False
            if iban:
                iban_acc = sepa.IBAN(iban)
                if iban_acc.valid:
                    new_acc_number = iban_acc.localized_BBAN
                    new_iban = str(iban_acc)
                elif iban != iban.upper():
                    new_iban = iban.upper
            if iban != new_iban or new_acc_number != acc_number:
                cursor.execute("UPDATE res_partner_bank "
                               "SET iban = '%s', acc_number = '%s' "
                               "WHERE id = %s" % (
                                   new_iban, new_acc_number, id
                               ))

    @staticmethod
    def _correct_IBAN(vals):
        '''
        Routine to correct IBAN values and deduce localized values when valid.
        Note: No check on validity IBAN/Country
        '''
        if 'iban' in vals and vals['iban']:
            iban = sepa.IBAN(vals['iban'])
            vals['iban'] = str(iban)
            vals['acc_number'] = iban.localized_BBAN
        return vals

    def create(self, cursor, uid, vals, context=None):
        '''
        Create dual function IBAN account for SEPA countries
        '''
        return self._founder.create(self, cursor, uid,
                                    self._correct_IBAN(vals), context
                                   )

    def write(self, cursor, uid, ids, vals, context=None):
        '''
        Create dual function IBAN account for SEPA countries
        '''
        return self._founder.write(self, cursor, uid, ids,
                                   self._correct_IBAN(vals), context
                                  )

    def search(self, cursor, uid, args, *rest, **kwargs):
        '''
        Overwrite search, as both acc_number and iban now can be filled, so
        the original base_iban 'search and search again fuzzy' tactic now can
        result in doubled findings. Also there is now enough info to search
        for local accounts when a valid IBAN was supplied.
        
        Chosen strategy: create complex filter to find all results in just
                         one search
        '''

        def is_term(arg):
            '''Flag an arg as term or otherwise'''
            return isinstance(arg, (list, tuple)) and len(arg) == 3

        def extended_filter_term(term):
            '''
            Extend the search criteria in term when appropriate.
            '''
            extra_term = None
            if term[0].lower() == 'iban' and term[1] in ('=', '=='):
                iban = sepa.IBAN(term[2])
                if iban.valid:
                    # Some countries can't convert to BBAN
                    try:
                        bban = iban.localized_BBAN
                        # Prevent empty search filters
                        if bban:
                            extra_term = ('acc_number', term[1], bban)
                    except:
                        pass
            if extra_term:
                return ['|', term, extra_term]
            return [term]

        def extended_search_expression(args):
            '''
            Extend the search expression in args when appropriate.
            The expression itself is in reverse polish notation, so recursion
            is not needed.
            '''
            if not args:
                return []

            all = []
            if is_term(args[0]) and len(args) > 1:
                # Classic filter, implicit '&'
                all += ['&']
            
            for arg in args:
                if is_term(arg):
                    all += extended_filter_term(arg)
                else:
                    all += arg
            return all

        # Extend search filter
        newargs = extended_search_expression(args)
        
        # Original search (_founder)
        results = self._founder.search(self, cursor, uid, newargs,
                                       *rest, **kwargs
                                      )
        return results

    def read(self, *args, **kwargs):
        '''
        Convert IBAN electronic format to IBAN display format
        '''
        records = self._founder.read(self, *args, **kwargs)
	if not isinstance(records, list):
            records = [records,]
        for record in records:
            if 'iban' in record and record['iban']:
                record['iban'] = unicode(sepa.IBAN(record['iban']))
        return records

    def check_iban(self, cursor, uid, ids):
        '''
        Check IBAN number
        '''
        for bank_acc in self.browse(cursor, uid, ids):
            if bank_acc.iban:
                iban = sepa.IBAN(bank_acc.iban)
                if not iban.valid:
                    return False
        return True

    def get_bban_from_iban(self, cursor, uid, ids, context=None):
        '''
        Return the local bank account number aka BBAN from the IBAN.
        '''
        for record in self.browse(cursor, uid, ids, context):
            if not record.iban:
                res[record.id] = False
            else:
                iban_acc = sepa.IBAN(record.iban)
                try:
                    res[record.id] = iban_acc.localized_BBAN
                except NotImplementedError:
                    res[record_id] = False
        return res

    def onchange_acc_number(self, cursor, uid, ids, acc_number,
                            partner_id, country_id, context=None
                           ):
        '''
        Trigger to find IBAN. When found:
            1. Reformat BBAN
            2. Autocomplete bank
        '''
        if not acc_number:
            return {}

        values = {}
        country_obj = self.pool.get('res.country')
        country_ids = []

        # Pre fill country based on available data. This is just a default
        # which can be overridden by the user.
        # 1. Use provided country_id (manually filled)
        if country_id:
            country = country_obj.browse(cursor, uid, country_id)
            country_ids = [country_id]
        # 2. Use country_id of found bank accounts
        # This can be usefull when there is no country set in the partners
        # addresses, but there was a country set in the address for the bank
        # account itself before this method was triggered.
        elif ids and len(ids) == 1:
            partner_bank_obj = self.pool.get('res.partner.bank')
            partner_bank_id = partner_bank_obj.browse(cursor, uid, ids[0])
            if partner_bank_id.country_id:
                country = partner_bank_id.country_id
                country_ids = [country.id]
        # 3. Use country_id of default address of partner
        # The country_id of a bank account is a one time default on creation.
        # It originates in the same address we are about to check, but
        # modifications on that address afterwards are not transfered to the
        # bank account, hence the additional check.
        elif partner_id:
            partner_obj = self.pool.get('res.partner')
            country = partner_obj.browse(cursor, uid, partner_id).country
            country_ids = country and [country.id] or []
        # 4. Without any of the above, take the country from the company of
        # the handling user
        if not country_ids:
            user = self.pool.get('res.users').browse(cursor, uid, uid)
            # Try users address first
            if user.address_id and user.address_id.country_id:
                country = user.address_id.country_id
                country_ids = [country.id]
            # Last try user companies partner
            elif (user.company_id and
                  user.company_id.partner_id and
                  user.company_id.partner_id.country
                 ):
                country_ids = [user.company_id.partner_id.country.id]
            else:
                if (user.company_id and user.company_id.partner_id and
                    user.company_id.partner_id.country):
                    country_ids =  [user.company_id.partner_id.country.id]
                else:
                    # Ok, tried everything, give up and leave it to the user
                    return warning(_('Insufficient data'),
                                   _('Insufficient data to select online '
                                     'conversion database')
                                   )
        result = {'value': values}
        # Complete data with online database when available
        if country.code in sepa.IBAN.countries:
            try:
                info = sepa.online.account_info(country.code, acc_number)
                if info:
                    iban_acc = sepa.IBAN(info.iban)
                    if iban_acc.valid:
                        values['acc_number'] = iban_acc.localized_BBAN
                        values['iban'] = unicode(iban_acc)
                        bank_id, country_id = get_or_create_bank(
                            self.pool, cursor, uid,
                            info.bic or iban_acc.BIC_searchkey,
                            code = info.code, name = info.bank
                            )
                        values['country_id'] = country_id or \
                                               country_ids and country_ids[0] or \
                                               False
                        values['bank'] = bank_id or False
                    else:
                        info = None
                if info is None:
                    result.update(warning(
                        _('Invalid data'),
                        _('The account number appears to be invalid for %(country)s')
                        % {'country': country.name}
                    ))
            except NotImplementedError:
                if country.code in sepa.IBAN.countries:
                    acc_number_fmt = sepa.BBAN(acc_number, country.code)
                    if acc_number_fmt.valid:
                        values['acc_number'] = str(acc_number_fmt)
                    else:
                        values['acc_number'] = acc_number
                        result.update(warning(
                            _('Invalid format'),
                            _('The account number has the wrong format for %(country)s')
                            % {'country': country.name}
                        ))
                else:
                    values['acc_number'] = acc_number
        return result

    def onchange_iban(self, cursor, uid, ids, iban, context=None):
        '''
        Trigger to verify IBAN. When valid:
            1. Extract BBAN as local account
            2. Auto complete bank
        '''
        if not iban:
            return {}

        iban_acc = sepa.IBAN(iban)
        if iban_acc.valid:
            bank_id, country_id = get_or_create_bank(
                self.pool, cursor, uid, iban_acc.BIC_searchkey,
                code=iban_acc.BIC_searchkey
                )
            return {
                'value': dict(
                    acc_number = iban_acc.localized_BBAN,
                    iban = unicode(iban_acc),
                    country = country_id or False,
                    bank = bank_id or False,
                )
            }
        return warning(_('Invalid IBAN account number!'),
                       _("The IBAN number doesn't seem to be correct")
                      )

    _constraints = [
        (check_iban, _("The IBAN number doesn't seem to be correct"), ["iban"])
    ]

res_partner_bank()

class res_bank(osv.osv):
    '''
    Add a on_change trigger to automagically fill bank details from the 
    online SWIFT database. Allow hand filled names to overrule SWIFT names.
    '''
    _inherit = 'res.bank'

    def onchange_bic(self, cursor, uid, ids, bic, name, context=None):
        '''
        Trigger to auto complete other fields.
        '''
        if not bic:
            return {}

        info, address = sepa.online.bank_info(bic)
        if not info:
            return {}

        if address and address.country_id:
            country_id = self.pool.get('res.country').search(
                cursor, uid, [('code','=',address.country_id)]
            )
            country_id = country_id and country_id[0] or False
        else:
            country_id = False

        return {
            'value': dict(
                # Only the first eight positions of BIC are used for bank
                # transfers, so ditch the rest.
                bic = info.bic[:8],
                code = info.code,
                street = address.street,
                street2 = 
                    address.has_key('street2') and address.street2 or False,
                zip = address.zip,
                city = address.city,
                country = country_id,
                name = name and name or info.name,
            )
        }

res_bank()

class invoice(osv.osv):
    '''
    Create other reference types as well.

    Descendant classes can extend this function to add more reference
    types, ie.

    def _get_reference_type(self, cr, uid, context=None):
        return super(my_class, self)._get_reference_type(cr, uid,
            context=context) + [('my_ref', _('My reference')]

    Don't forget to redefine the column "reference_type" as below or
    your method will never be triggered.
    '''
    _inherit = 'account.invoice'

    def _get_reference_type(self, cr, uid, context=None):
        '''
        Return the list of reference types
        '''
        return [('none', _('Free Reference')),
                ('structured', _('Structured Reference')),
               ]

    _columns = {
        'reference_type': fields.selection(_get_reference_type,
                                           'Reference Type', required=True
                                          )
    }

invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
