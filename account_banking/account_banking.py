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

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp import netsvc, SUPERUSER_ID
from openerp.addons.decimal_precision import decimal_precision as dp
from openerp.addons.account_banking import sepa
from openerp.addons.account_banking.wizard.banktools import get_or_create_bank

def warning(title, message):
    '''Convenience routine'''
    return {'warning': {'title': title, 'message': message}}


class account_banking_account_settings(orm.Model):
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
            cr, uid, company_id, ['partner_id'],
            context=context)['partner_id'][0]
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

    def _default_credit_account_id(
            self, cr, uid, context=None, company_id=False):
        localcontext = context and context.copy() or {}
        localcontext['force_company'] = (
            company_id or self._default_company(cr, uid, context=context))
        account_def = self.pool.get('ir.property').get(
            cr, uid, 'property_account_payable',
            'res.partner', context=localcontext)
        return account_def and account_def.id or False

    def find(self, cr, uid, journal_id, partner_bank_id=False, context=None):
        domain = [('journal_id', '=', journal_id)]
        if partner_bank_id:
            domain.append(('partner_bank_id', '=', partner_bank_id))
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
    }
account_banking_account_settings()


class account_banking_imported_file(orm.Model):
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
        'date': fields.date.context_today,
        'user_id': lambda self, cr, uid, context: uid,
    }
account_banking_imported_file()


class account_bank_statement(orm.Model):
    '''
    Implement changes to this model for the following features:

    * bank statement lines have their own period_id, derived from
    their effective date. The period and date are propagated to
    the move lines created from each statement line
    * bank statement lines have their own state. When a statement
    is confirmed, all lines are confirmed too. When a statement
    is reopened, lines remain confirmed until reopened individually.
    * upon confirmation of a statement line, the move line is
    created and reconciled according to the matched entry(/ies)
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
        'period_id': False,
    }

    def _check_company_id(self, cr, uid, ids, context=None):
        """
        Adapt this constraint method from the account module to reflect the
        move of period_id to the statement line
        """
        for statement in self.browse(cr, uid, ids, context=context):
            for line in statement.line_ids:
                if (line.period_id and
                    statement.company_id.id != line.period_id.company_id.id):
                    return False
                if not statement.period_id:
                    statement.write({'period_id': line.period_id.id})
        return super(account_bank_statement, self)._check_company_id(
            cr, uid, ids, context=context)
    
    # Redefine the constraint, or it still refer to the original method
    _constraints = [
        (_check_company_id,
         'The journal and period chosen have to belong to the same company.',
         ['journal_id','period_id']),
        ]

    def _get_period(self, cr, uid, date, context=None):
        '''
        Find matching period for date, not meant for _defaults.
        '''
        period_obj = self.pool.get('account.period')
        periods = period_obj.find(cr, uid, dt=date, context=context)
        return periods and periods[0] or False

    def _prepare_move(
            self, cr, uid, st_line, st_line_number, context=None):
        """
        Add the statement line's period to the move, overwriting
        the period on the statement
        """
        res = super(account_bank_statement, self)._prepare_move(
            cr, uid, st_line, st_line_number, context=context)
        if context and context.get('period_id'):
            res['period_id'] = context['period_id']
        return res

    def _prepare_move_line_vals(
            self, cr, uid, st_line, move_id, debit, credit, currency_id=False,
            amount_currency=False, account_id=False, analytic_id=False,
            partner_id=False, context=None):
        """
        Add the statement line's period to the move lines, overwriting
        the period on the statement
        """
        res = super(account_bank_statement, self)._prepare_move_line_vals(
            cr, uid, st_line, move_id, debit, credit, currency_id=currency_id,
            amount_currency=amount_currency, account_id=account_id,
            analytic_id=analytic_id, partner_id=partner_id, context=context)
        if context and context.get('period_id'):
            res['period_id'] = context['period_id']
        return res

    def create_move_from_st_line(self, cr, uid, st_line_id,
                                 company_currency_id, st_line_number,
                                 context=None):
        if context is None:
            context = {}
        account_move_obj = self.pool.get('account.move')
        account_move_line_obj = self.pool.get('account.move.line')
        account_bank_statement_line_obj = self.pool.get(
            'account.bank.statement.line')
        st_line = account_bank_statement_line_obj.browse(
            cr, uid, st_line_id, context=context)

        # Take period from statement line and write to context
        # this will be picked up by the _prepare_move* methods
        period_id = self._get_period(
            cr, uid, st_line.date, context=context)
        localctx = context.copy()
        localctx['period_id'] = period_id

        # Write date & period on the voucher, delegate to account_voucher's
        # override of this method. Then post the related move and return.
        if st_line.voucher_id:
            voucher_pool = self.pool.get('account.voucher')
            voucher_pool.write(
                cr, uid, [st_line.voucher_id.id], {
                    'date': st_line.date,
                    'period_id': period_id,
                }, context=context)

        res = super(account_bank_statement, self).create_move_from_st_line(
            cr, uid, st_line_id, company_currency_id, st_line_number,
            context=localctx)

        st_line.refresh()
        if st_line.voucher_id:
            if not st_line.voucher_id.journal_id.entry_posted:
                account_move_obj.post(
                    cr, uid, [st_line.voucher_id.move_id.id], context={})
        else:
            # Write stored reconcile_id and pay invoices through workflow 
            if st_line.reconcile_id:
                move_ids = [move.id for move in st_line.move_ids]
                torec = account_move_line_obj.search(
                    cr, uid, [
                        ('move_id', 'in', move_ids),
                        ('account_id', '=', st_line.account_id.id)],
                    context=context)
                account_move_line_obj.write(cr, uid, torec, {
                        (st_line.reconcile_id.line_partial_ids and 
                         'reconcile_partial_id' or 'reconcile_id'): 
                        st_line.reconcile_id.id }, context=context)
                for move_line in (st_line.reconcile_id.line_id or []) + (
                    st_line.reconcile_id.line_partial_ids or []):
                    netsvc.LocalService("workflow").trg_trigger(
                        uid, 'account.move.line', move_line.id, cr)
        return res

    def button_confirm_bank(self, cr, uid, ids, context=None):
        """
        Assign journal sequence to statements without a name
        """
        if context is None:
            context = {}
        obj_seq = self.pool.get('ir.sequence')
        if ids and isinstance(ids, (int, long)):
            ids = [ids]
        noname_ids = self.search(
            cr, uid, [('id', 'in', ids),('name', '=', '/')],
            context=context)
        for st in self.browse(cr, uid, noname_ids, context=context):
            if st.journal_id.sequence_id:
                period_id = self._get_period(cr, uid, st.date)
                year = self.pool.get('account.period').browse(
                    cr, uid, period_id, context=context).fiscalyear_id.id
                c = {'fiscalyear_id': year}
                st_number = obj_seq.get_id(
                    cr, uid, st.journal_id.sequence_id.id, context=c)
                self.write(
                    cr, uid, ids, {'name': st_number}, context=context)
        
        return super(account_bank_statement, self).button_confirm_bank(
            cr, uid, ids, context)

account_bank_statement()


class account_voucher(orm.Model):
    _inherit = 'account.voucher'

    def _get_period(self, cr, uid, context=None):
        if context is None:
            context = {}
        if not context.get('period_id') and context.get('move_line_ids'):
            return self.pool.get('account.move.line').browse(
                cr, uid , context.get('move_line_ids'), context=context)[0].period_id.id
        return super(account_voucher, self)._get_period(cr, uid, context)

account_voucher()


class account_bank_statement_line(orm.Model):
    '''
    Extension on basic class:
        1. Extra links to account.period and res.partner.bank for tracing and
           matching.
        2. Extra 'trans' field to carry the transaction id of the bank.
        3. Readonly states for most fields except when in draft.
    '''
    _inherit = 'account.bank.statement.line'
    _description = 'Bank Transaction'

    def _get_period(self, cr, uid, context=None):
        date = context.get('date', None)
        periods = self.pool.get('account.period').find(cr, uid, dt=date)
        return periods and periods[0] or False

    def _get_currency(self, cr, uid, context=None):
        '''
        Get the default currency (required to allow other modules to function,
        which assume currency to be a calculated field and thus optional)
        Remark: this is only a fallback as the real default is in the journal,
        which is inaccessible from within this method.
        '''
        res_users_obj = self.pool.get('res.users')
        return res_users_obj.browse(cr, uid, uid,
                context=context).company_id.currency_id.id

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
        # Redefines. Todo: refactor away to view attrs
        'amount': fields.float('Amount', readonly=True,
                            digits_compute=dp.get_precision('Account'),
                            states={'draft': [('readonly', False)]}),
        'ref': fields.char('Ref.', size=32, readonly=True,
                            states={'draft': [('readonly', False)]}),
        'name': fields.char('Name', size=64, required=False, readonly=True,
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
                            states={'confirmed': [('readonly', True)]}),
        'currency': fields.many2one('res.currency', 'Currency', required=True,
                            states={'confirmed': [('readonly', True)]}),
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
        'currency': _get_currency,
    }

account_bank_statement_line()


class res_partner_bank(orm.Model):
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
            if mro[i].__module__.startswith('openerp.addons.base.'):
                self._founder = mro[i]
                break

    def init(self, cr):
        '''
        Update existing iban accounts to comply to new regime
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

    def create(self, cr, uid, vals, context=None):
        '''
        Create dual function IBAN account for SEPA countries
        '''
        if vals.get('state') == 'iban':
            iban = (vals.get('acc_number')
                    or vals.get('acc_number_domestic', False))
            vals['acc_number'], vals['acc_number_domestic'] = (
                self._correct_IBAN(iban))
        return self._founder.create(self, cr, uid, vals, context)

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
            self._founder.write(self, cr, uid, account['id'], vals, context)
        return True

    def search(self, cr, uid, args, *rest, **kwargs):
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
        
        # Original search
        results = super(res_partner_bank, self).search(
            cr, uid, newargs, *rest, **kwargs)
        return results

    def read(
        self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        '''
        Convert IBAN electronic format to IBAN display format
        SR 2012-02-19: do we really need this? Fields are converted upon write already.
        '''
        if fields and 'state' not in fields:
            fields.append('state')
        records = self._founder.read(self, cr, uid, ids, fields, context, load)
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

    def check_iban(self, cr, uid, ids, context=None):
        '''
        Check IBAN number
        '''
        for bank_acc in self.browse(cr, uid, ids, context=context):
            if bank_acc.state == 'iban' and bank_acc.acc_number:
                iban = sepa.IBAN(bank_acc.acc_number)
                if not iban.valid:
                    return False
        return True

    def get_bban_from_iban(self, cr, uid, ids, context=None):
        '''
        Return the local bank account number aka BBAN from the IBAN.
        '''
        res = {}
        for record in self.browse(cr, uid, ids, context):
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
        self, cr, uid, ids, acc_number,
        partner_id, country_id, context=None):
        '''
        Trigger to find IBAN. When found:
            1. Reformat BBAN
            2. Autocomplete bank

        TODO: prevent unnecessary assignment of country_ids and
        browsing of the country
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
            country = country_obj.browse(cr, uid, country_id, context=context)
            country_ids = [country_id]
        # 2. Use country_id of found bank accounts
        # This can be usefull when there is no country set in the partners
        # addresses, but there was a country set in the address for the bank
        # account itself before this method was triggered.
        elif ids and len(ids) == 1:
            partner_bank_obj = self.pool.get('res.partner.bank')
            partner_bank_id = partner_bank_obj.browse(cr, uid, ids[0], context=context)
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
            country = partner_obj.browse(cr, uid, partner_id, context=context).country
            country_ids = country and [country.id] or []
        # 4. Without any of the above, take the country from the company of
        # the handling user
        if not country_ids:
            user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
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
                cr, uid, country_ids[0], context=context)
            values['country_id'] = country_ids[0]
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
                            self.pool, cr, uid,
                            info.bic or iban_acc.BIC_searchkey,
                            name = info.bank
                            )
                        if country_id:
                            values['country_id'] = country_id
                        values['bank'] = bank_id or False
                        if info.bic:
                            values['bank_bic'] = info.bic
                    else:
                        info = None
                if info is None:
                    result.update(warning(
                        _('Invalid data'),
                        _('The account number appears to be invalid for %s')
                        % country.name
                    ))
            except NotImplementedError:
                if country.code in sepa.IBAN.countries:
                    acc_number_fmt = sepa.BBAN(acc_number, country.code)
                    if acc_number_fmt.valid:
                        values['acc_number_domestic'] = str(acc_number_fmt)
                    else:
                        result.update(warning(
                            _('Invalid format'),
                            _('The account number has the wrong format for %s')
                            % country.name
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

res_partner_bank()


class res_bank(orm.Model):
    '''
    Add a on_change trigger to automagically fill bank details from the 
    online SWIFT database. Allow hand filled names to overrule SWIFT names.
    '''
    _inherit = 'res.bank'

    def onchange_bic(self, cr, uid, ids, bic, name, context=None):
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
                cr, uid, [('code','=',address.country_id)]
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


class invoice(orm.Model):
    '''
    Create other reference types as well.

    Descendant classes can extend this function to add more reference
    types, ie.

    def _get_reference_type(self, cr, uid, context=None):
        return super(my_class, self)._get_reference_type(cr, uid,
            context=context) + [('my_ref', _('My reference')]

    Don't forget to redefine the column "reference_type" as below or
    your method will never be triggered.

    TODO: move 'structured' part to account_banking_payment module
    where it belongs
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


class account_move_line(orm.Model):
    _inherit = "account.move.line"

    def get_balance(self, cr, uid, ids, context=None):
        """ 
        Return the balance of any set of move lines.

        Not to be confused with the 'balance' field on this model, which
        returns the account balance that the move line applies to.
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
