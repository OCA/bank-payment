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
import sepa
from osv import osv, fields
from tools.translate import _
from wizard.banktools import get_or_create_bank
import decimal_precision as dp
import netsvc
from openerp import SUPERUSER_ID

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
        'partner_id': fields.related(
            'company_id', 'partner_id',
            type='many2one', relation='res.partner',
            string='Partner'),
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

    def _default_company(self, cr, uid, context=None):
        """
        Return the user's company or the first company found
        in the database
        """
        user = self.pool.get('res.users').read(
            cr, uid, uid, ['company_id'], context=context)
        if user['company_id']:
            return user['company_id'][0]
        return self.pool.get('res.company').search(
            cr, uid, [('parent_id', '=', False)])[0]
    
    def _default_partner_id(self, cr, uid, context=None, company_id=False):
        if not company_id:
            company_id = self._default_company(cr, uid, context=context)
        return self.pool.get('res.company').read(
            cr, uid, company_id, ['partner_id'],
            context=context)['partner_id'][0]

    def _default_journal(self, cr, uid, context=None, company_id=False):
        if not company_id:
            company_id = self._default_company(cr, uid, context=context)
        journal_ids = self.pool.get('account.journal').search(
            cr, uid, [('type', '=', 'bank'), ('company_id', '=', company_id)])
        return journal_ids and journal_ids[0] or False

    def _default_partner_bank_id(
            self, cr, uid, context=None, company_id=False):
        if not company_id:
            company_id = self._default_company(cr, uid, context=context)
        partner_id = self.pool.get('res.company').read(
            cr, uid, company_id, ['partner_id'], context=context)['partner_id'][0]
        bank_ids = self.pool.get('res.partner.bank').search(
            cr, uid, [('partner_id', '=', partner_id)], context=context)
        return bank_ids and bank_ids[0] or False

    def _default_debit_account_id(
            self, cr, uid, context=None, company_id=False):
        localcontext = context and context.copy() or {}
        localcontext['force_company'] = (
            company_id or self._default_company(cr, uid, context=context))
        account_def = self.pool.get('ir.property').get(
            cr, uid, 'property_account_receivable',
            'res.partner', context=localcontext)
        return account_def and account_def.id or False

    def _default_credit_account_id(self, cr, uid, context=None, company_id=False):
        localcontext = context and context.copy() or {}
        localcontext['force_company'] = (
            company_id or self._default_company(cr, uid, context=context))
        account_def = self.pool.get('ir.property').get(
            cr, uid, 'property_account_payable',
            'res.partner', context=localcontext)
        return account_def and account_def.id or False

    def find(self, cr, uid, journal_id, partner_bank_id=False, context=None):
        domain = [('journal_id','=',journal_id)]
        if partner_bank_id:
            domain.append(('partner_bank_id','=',partner_bank_id))
        return self.search(cr, uid, domain, context=context)

    def onchange_partner_bank_id(
            self, cr, uid, ids, partner_bank_id, context=None):
        values = {}
        if partner_bank_id:
            bank = self.pool.get('res.partner.bank').read(
                cr, uid, partner_bank_id, ['journal_id'], context=context)
            if bank['journal_id']:
                values['journal_id'] = bank['journal_id'][0]
        return {'value': values}

    def onchange_company_id (
            self, cr, uid, ids, company_id=False, context=None):
        if not company_id:
            return {}
        result = {
            'partner_id': self._default_partner_id(
                cr, uid, company_id=company_id, context=context),
            'journal_id': self._default_journal(
                cr, uid, company_id=company_id, context=context),
            'default_debit_account_id': self._default_debit_account_id(
                cr, uid, company_id=company_id, context=context),
            'default_credit_account_id': self._default_credit_account_id(
                cr, uid, company_id=company_id, context=context),
            }
        return {'value': result}

    _defaults = {
        'company_id': _default_company,
        'partner_id': _default_partner_id,
        'journal_id': _default_journal,
        'default_debit_account_id': _default_debit_account_id,
        'default_credit_account_id': _default_credit_account_id,
        'partner_bank_id': _default_partner_bank_id,
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
                                states={'draft': [('readonly', False)]}
                               ),
        'format': fields.char('File Format', size=20, readonly=True,
                              states={'draft': [('readonly', False)]}
                             ),
        'file': fields.binary('Raw Data', readonly=True,
                              states={'draft': [('readonly', False)]}
                             ),
        'log': fields.text('Import Log', readonly=True,
                           states={'draft': [('readonly', False)]}
                          ),
        'user_id': fields.many2one('res.users', 'Responsible User',
                                   readonly=True, select=True,
                                   states={'draft': [('readonly', False)]}
                                  ),
        'state': fields.selection(
            [('unfinished', 'Unfinished'),
             ('error', 'Error'),
             ('review', 'Review'),
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

    def _check_company_id(self, cr, uid, ids, context=None):
        """
        Adapt this constraint method from the account module to reflect the
        move of period_id to the statement line
        """
        for statement in self.browse(cr, uid, ids, context=context):
            if (statement.period_id and
                statement.company_id.id != statement.period_id.company_id.id):
                return False
            for line in statement.line_ids:
                if (line.period_id and
                    statement.company_id.id != line.period_id.company_id.id):
                    return False
        return True
    
    # Redefine the constraint, or it still refer to the original method
    _constraints = [
        (_check_company_id, 'The journal and period chosen have to belong to the same company.', ['journal_id','period_id']),
    ]

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
        # Modifications by account_voucher are merged below.
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
        st_line = account_bank_statement_line_obj.browse(
            cr, uid, st_line_id, context=context)
        period_id = self._get_period(
            cr, uid, st_line.date, context=context)    # AB
        # Start account voucher
        # Post the voucher and update links between statement and moves
        if st_line.voucher_id:
            voucher_pool = self.pool.get('account.voucher')
            wf_service = netsvc.LocalService("workflow")
            voucher_pool.write(
                cr, uid, [st_line.voucher_id.id], {
                    'number': st_line_number,
                    'date': st_line.date,
                    'period_id': period_id, # AB
                }, context=context)
            if st_line.voucher_id.state == 'cancel':
                voucher_pool.action_cancel_draft(
                    cr, uid, [st_line.voucher_id.id], context=context)
            wf_service.trg_validate(
                uid, 'account.voucher', st_line.voucher_id.id, 'proforma_voucher', cr)
            v = voucher_pool.browse(
                cr, uid, st_line.voucher_id.id, context=context)
            account_bank_statement_line_obj.write(cr, uid, [st_line_id], {
                    'move_ids': [(4, v.move_id.id, False)]
                    })
            account_move_line_obj.write(
                cr, uid, [x.id for x in v.move_ids],
                {'statement_id': st_line.statement_id.id}, context=context)
            # End of account_voucher
            st_line.refresh()

            # AB: The voucher journal isn't automatically posted, so post it (if needed)
            if not st_line.voucher_id.journal_id.entry_posted:
                account_move_obj.post(cr, uid, [st_line.voucher_id.move_id.id], context={})
            return True

        st = st_line.statement_id

        context.update({'date': st_line.date})
        ctxt = context.copy()                       # AB
        ctxt['company_id'] = st_line.company_id.id  # AB

        move_id = account_move_obj.create(cr, uid, {
            'journal_id': st.journal_id.id,
            'period_id': period_id, # AB
            'date': st_line.date,
            'name': st_line_number,
        }, context=context)
        account_bank_statement_line_obj.write(cr, uid, [st_line.id], {
            'move_ids': [(4, move_id, False)]
        })

        torec = []
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
        torec.append(move_line_id)

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

        Does not apply to voucher integration, but only to
        payments and payment orders
        """
        if st_line.reconcile_id:
            account_move_line_obj.write(cr, uid, torec, {
                    (st_line.reconcile_id.line_partial_ids and 
                     'reconcile_partial_id' or 'reconcile_id'): 
                    st_line.reconcile_id.id }, context=context)
            for move_line in (st_line.reconcile_id.line_id or []) + (
                st_line.reconcile_id.line_partial_ids or []):
                netsvc.LocalService("workflow").trg_trigger(
                    uid, 'account.move.line', move_line.id, cr)
        #""" End account-banking """

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
            for move_line in (
                    st_line.reconcile_id and
                    (st_line.reconcile_id.line_id or
                     st_line.reconcile_id.line_partial_ids) or
                    st_line.import_transaction_id and 
                    st_line.import_transaction_id.move_line_id and
                    [st_line.import_transaction_id.move_line_id] or []):
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
                            states={'confirmed': [('readonly', True)]}),
        'currency': fields.many2one('res.currency', 'Currency', required=True,
                            states={'confirmed': [('readonly', True)]}),

        # Not used yet, but usefull in the future.
        'international': fields.boolean('International Transaction',
                            required=False,
                            states={'confirmed': [('readonly', True)]},
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

    def init(self, cr):
        '''
        Update existing iban accounts to comply to new regime
        Note that usage of the ORM is not possible here, as the ORM cannot
        search on values not provided by the client.
        '''
        
        partner_bank_obj = self.pool.get('res.partner.bank')
        bank_ids = partner_bank_obj.search(
            cr, SUPERUSER_ID, [('state', '=', 'iban')], limit=0)
        for bank in partner_bank_obj.read(cr, SUPERUSER_ID, bank_ids):
            write_vals = {}
            if bank['state'] == 'iban':
                iban_acc = sepa.IBAN(bank['acc_number'])
                if iban_acc.valid:
                    write_vals['acc_number_domestic'] = iban_acc.localized_BBAN
                    write_vals['acc_number'] = str(iban_acc)
                elif bank['acc_number'] != bank['acc_number'].upper():
                    write_vals['acc_number'] = bank['acc_number'].upper()
                if write_vals:
                    partner_bank_obj.write(
                        cr, SUPERUSER_ID, bank['id'], write_vals)

    @staticmethod
    def _correct_IBAN(acc_number):
        '''
        Routine to correct IBAN values and deduce localized values when valid.
        Note: No check on validity IBAN/Country
        '''
        iban = sepa.IBAN(acc_number)
        return (str(iban), iban.localized_BBAN)

    def create(self, cursor, uid, vals, context=None):
        '''
        Create dual function IBAN account for SEPA countries
        '''
        if vals.get('state') == 'iban':
            iban = vals.get('acc_number',False) or vals.get('acc_number_domestic',False)
            vals['acc_number'], vals['acc_number_domestic'] = (
                self._correct_IBAN(iban))
        return self._founder.create(cursor, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        '''
        Create dual function IBAN account for SEPA countries
        
        Update the domestic account number when the IBAN is
        written, or clear the domestic number on regular account numbers.
        '''
        if ids and isinstance(ids, (int, long)):
            ids = [ids]
        for account in self.read(
            cr, uid, ids, ['state', 'acc_number']):
            if 'state' in vals or 'acc_number' in vals:
                account.update(vals)
                if account['state'] == 'iban':
                    vals['acc_number'], vals['acc_number_domestic'] = (
                        self._correct_IBAN(account['acc_number']))
                else:
                    vals['acc_number_domestic'] = False
            self._founder.write(cr, uid, account['id'], vals, context)
        return True

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
            if term[0].lower() == 'acc_number' and term[1] in ('=', '=='):
                iban = sepa.IBAN(term[2])
                if iban.valid:
                    # Some countries can't convert to BBAN
                    try:
                        bban = iban.localized_BBAN
                        # Prevent empty search filters
                        if bban:
                            extra_term = ('acc_number_domestic', term[1], bban)
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
        results = self._founder.search(cursor, uid, newargs,
                                       *rest, **kwargs
                                      )
        return results

    def read(
        self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        '''
        Convert IBAN electronic format to IBAN display format
        SR 2012-02-19: do we really need this? Fields are converted upon write already.
        '''
        if fields and 'state' not in fields:
            fields.append('state')
        records = self._founder.read(cr, uid, ids, fields, context, load)
        is_list = True
        if not isinstance(records, list):
            records = [records,]
            is_list = False
        for record in records:
            if 'acc_number' in record and record['state'] == 'iban':
                record['acc_number'] = unicode(sepa.IBAN(record['acc_number']))
        if is_list:
            return records
        return records[0]

    def check_iban(self, cursor, uid, ids):
        '''
        Check IBAN number
        '''
        for bank_acc in self.browse(cursor, uid, ids):
            if bank_acc.state == 'iban' and bank_acc.acc_number:
                iban = sepa.IBAN(bank_acc.acc_number)
                if not iban.valid:
                    return False
        return True

    def get_bban_from_iban(self, cursor, uid, ids, context=None):
        '''
        Return the local bank account number aka BBAN from the IBAN.
        '''
        res = {}
        for record in self.browse(cursor, uid, ids, context):
            if not record.state == 'iban':
                res[record.id] = False
            else:
                iban_acc = sepa.IBAN(record.acc_number)
                try:
                    res[record.id] = iban_acc.localized_BBAN
                except NotImplementedError:
                    res[record.id] = False
        return res

    def onchange_acc_number(
        self, cr, uid, ids, acc_number, acc_number_domestic,
        state, partner_id, country_id, context=None):
        if state == 'iban':
            return self.onchange_iban(
                cr, uid, ids, acc_number, acc_number_domestic,
                state, partner_id, country_id, context=None
                )
        else:
            return self.onchange_domestic(
                cr, uid, ids, acc_number,
                partner_id, country_id, context=None
                )

    def onchange_domestic(
        self, cursor, uid, ids, acc_number,
        partner_id, country_id, context=None):
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
        country = False

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
            # Try user companies partner (user no longer has address in 6.1)
            if (user.company_id and
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
        if country_ids:
            country = country_obj.browse(
                cursor, uid, country_ids[0], context=context)
        if country and country.code in sepa.IBAN.countries:
            try:
                info = sepa.online.account_info(country.code, acc_number)
                if info:
                    iban_acc = sepa.IBAN(info.iban)
                    if iban_acc.valid:
                        values['acc_number_domestic'] = iban_acc.localized_BBAN
                        values['acc_number'] = unicode(iban_acc)
                        values['state'] = 'iban'
                        bank_id, country_id = get_or_create_bank(
                            self.pool, cursor, uid,
                            info.bic or iban_acc.BIC_searchkey,
                            name = info.bank
                            )
                        values['country_id'] = country_id or \
                                               country_ids and country_ids[0] or \
                                               False
                        values['bank'] = bank_id or False
                        if info.bic:
                            values['bank_bic'] = info.bic
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
                        values['acc_number_domestic'] = str(acc_number_fmt)
                    else:
                        result.update(warning(
                            _('Invalid format'),
                            _('The account number has the wrong format for %(country)s')
                            % {'country': country.name}
                        ))
        return result

    def onchange_iban(
        self, cr, uid, ids, acc_number, acc_number_domestic,
        state, partner_id, country_id, context=None):
        '''
        Trigger to verify IBAN. When valid:
            1. Extract BBAN as local account
            2. Auto complete bank
        '''
        if not acc_number:
            return {}

        iban_acc = sepa.IBAN(acc_number)
        if iban_acc.valid:
            bank_id, country_id = get_or_create_bank(
                self.pool, cr, uid, iban_acc.BIC_searchkey,
                code=iban_acc.BIC_searchkey
                )
            return {
                'value': dict(
                    acc_number_domestic = iban_acc.localized_BBAN,
                    acc_number = unicode(iban_acc),
                    country = country_id or False,
                    bank = bank_id or False,
                )
            }
        return warning(_('Invalid IBAN account number!'),
                       _("The IBAN number doesn't seem to be correct")
                      )

    _constraints = [
        # Cannot have this as a constraint as it is rejecting valid numbers from GB and DE
        # It works much better without this constraint!
        #(check_iban, _("The IBAN number doesn't seem to be correct"), ["acc_number"])
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

    def test_undo_paid(self, cr, uid, ids, context=None):
        """ 
        Called from the workflow. Used to unset paid state on
        invoices that were paid with bank transfers which are being cancelled 
        """
        for invoice in self.read(cr, uid, ids, ['reconciled'], context):
            if invoice['reconciled']:
                return False
        return True

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

class account_move_line(osv.osv):
    _inherit = "account.move.line"

    def get_balance(self, cr, uid, ids, context=None):
        """ 
        Return the balance of any set of move lines.
        Surely this exists somewhere in account base, but I missed it.
        """
        total = 0.0
        if not ids:
            return total
        for line in self.read(
            cr, uid, ids, ['debit', 'credit'], context=context):
            total += (line['debit'] or 0.0) - (line['credit'] or 0.0)
        return total
account_move_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
