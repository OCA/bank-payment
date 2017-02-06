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
from openerp.osv.osv import except_osv
from openerp.tools.translate import _
from openerp import netsvc


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
            help=('The account to use when an unexpected payment was signaled.'
                  ' This can happen when a direct debit payment is cancelled '
                  'by a customer, or when no matching payment can be found. '
                  'Mind that you can correct movements before confirming them.'
                  ),
            required=True
        ),
        'default_debit_account_id': fields.many2one(
            'account.account', 'Default debit account',
            select=True, required=True,
            help=('The account to use when an unexpected payment is received. '
                  'This can be needed when a customer pays in advance or when '
                  'no matching invoice can be found. Mind that you can '
                  'correct movements before confirming them.'
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

    def onchange_company_id(
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
        'company_id': fields.many2one(
            'res.company',
            'Company',
            select=True,
            readonly=True,
        ),
        'date': fields.datetime(
            'Import Date',
            readonly=True,
            select=True,
            states={'draft': [('readonly', False)]},
        ),
        'format': fields.char(
            'File Format',
            size=20,
            readonly=True,
            states={'draft': [('readonly', False)]},
        ),
        'file': fields.binary(
            'Raw Data',
            readonly=True,
            states={'draft': [('readonly', False)]},
        ),
        'file_name': fields.char('File name', size=256),
        'log': fields.text(
            'Import Log',
            readonly=True,
            states={'draft': [('readonly', False)]},
        ),
        'user_id': fields.many2one(
            'res.users',
            'Responsible User',
            readonly=True,
            select=True,
            states={'draft': [('readonly', False)]},
        ),
        'state': fields.selection(
            [
                ('unfinished', 'Unfinished'),
                ('error', 'Error'),
                ('review', 'Review'),
                ('ready', 'Finished'),
            ],
            'State',
            select=True,
            readonly=True,
        ),
        'statement_ids': fields.one2many(
            'account.bank.statement',
            'banking_id',
            'Statements',
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
        'period_id': fields.many2one(
            'account.period',
            'Period',
            required=False,
            readonly=True,
        ),
        'banking_id': fields.many2one(
            'account.banking.imported.file',
            'Imported File',
            readonly=True,
        ),
    }

    _defaults = {
        'period_id': False,
    }

    def _check_company_id(self, cr, uid, ids, context=None):
        """
        Adapt this constraint method from the account module to reflect the
        move of period_id to the statement line: also check the periods of the
        lines. Update the statement period if it does not have one yet.
        Don't call super, because its check is integrated below and
        it will break if a statement does not have any lines yet and
        therefore may not have a period.
        """
        for statement in self.browse(cr, uid, ids, context=context):
            if (statement.period_id and
                    statement.company_id != statement.period_id.company_id):
                return False
            for line in statement.line_ids:
                if (line.period_id and
                        statement.company_id != line.period_id.company_id):
                    return False
                if not statement.period_id:
                    statement.write({'period_id': line.period_id.id})
                    statement.refresh()
        return True

    # Redefine the constraint, or it still refer to the original method
    _constraints = [
        (_check_company_id,
         'The journal and period chosen have to belong to the same company.',
         ['journal_id', 'period_id']),
    ]

    def _get_period(self, cr, uid, date=False, context=None):
        """
        Used in statement line's _defaults, so it is always triggered
        on installation or module upgrade even if there are no records
        without a value. For that reason, we need
        to be tolerant and allow for the situation in which no period
        exists for the current date (i.e. when no date is specified).

        Cannot be used directly as a defaults method due to lp:1296229
        """
        local_ctx = dict(context or {}, account_period_prefer_normal=True)
        try:
            return self.pool.get('account.period').find(
                cr, uid, dt=date, context=local_ctx)[0]
        except except_osv:
            if date:
                raise
        return False

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
            cr, uid, date=st_line.date, context=context)
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
                     'reconcile_partial_id' or
                     'reconcile_id'): st_line.reconcile_id.id
                }, context=context)
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
            cr, uid, [('id', 'in', ids), ('name', '=', '/')],
            context=context)
        for st in self.browse(cr, uid, noname_ids, context=context):
            if st.journal_id.sequence_id:
                period_id = self._get_period(
                    cr, uid, date=st.date, context=context)
                year = self.pool.get('account.period').browse(
                    cr, uid, period_id, context=context).fiscalyear_id.id
                c = {'fiscalyear_id': year}
                st_number = obj_seq.get_id(
                    cr, uid, st.journal_id.sequence_id.id, context=c)
                self.write(
                    cr, uid, ids, {'name': st_number}, context=context)

        return super(account_bank_statement, self).button_confirm_bank(
            cr, uid, ids, context)


class account_voucher(orm.Model):
    _inherit = 'account.voucher'

    def _get_period(self, cr, uid, context=None):
        if context is None:
            context = {}
        if not context.get('period_id') and context.get('move_line_ids'):
            move_line = self.pool.get('account.move.line').browse(
                cr, uid, context.get('move_line_ids')[0], context=context)
            return move_line.period_id.id
        return super(account_voucher, self)._get_period(cr, uid, context)


class account_bank_statement_line(orm.Model):
    '''
    Extension on basic class:
        1. Extra links to account.period and res.partner.bank for tracing and
           matching.
        2. Extra 'trans' field to carry the transaction id of the bank.
    '''
    _inherit = 'account.bank.statement.line'
    _description = 'Bank Transaction'

    def _get_period(self, cr, uid, date=False, context=None):
        return self.pool['account.bank.statement']._get_period(
            cr, uid, date=date, context=context)

    def _get_period_context(self, cr, uid, context=None):
        """
        Workaround for lp:1296229, context is passed positionally
        """
        return self._get_period(cr, uid, context=context)

    def _get_currency(self, cr, uid, context=None):
        '''
        Get the default currency (required to allow other modules to function,
        which assume currency to be a calculated field and thus optional)
        Remark: this is only a fallback as the real default is in the journal,
        which is inaccessible from within this method.
        '''
        res_users_obj = self.pool.get('res.users')
        return res_users_obj.browse(
            cr, uid, uid, context=context).company_id.currency_id.id

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
        # Only name left because of required False. Is this needed?
        'name': fields.char(
            'Name',
            size=64,
            required=False,
        ),
        # New columns
        'trans': fields.char(
            'Bank Transaction ID',
            size=15,
            required=False,
        ),
        'partner_bank_id': fields.many2one(
            'res.partner.bank',
            'Bank Account',
            required=False,
        ),
        'period_id': fields.many2one(
            'account.period',
            'Period',
        ),
        'currency': fields.many2one(
            'res.currency',
            'Currency',
            required=True,
        ),
        'reconcile_id': fields.many2one(
            'account.move.reconcile',
            'Reconciliation',
            readonly=True,
        ),
        'invoice_id': fields.function(
            _get_invoice_id,
            method=True,
            string='Linked Invoice',
            type='many2one',
            relation='account.invoice',
        ),
    }

    _defaults = {
        'period_id': _get_period_context,
        'currency': _get_currency,
    }


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
