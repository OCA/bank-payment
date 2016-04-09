# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2012 - 2013 Therp BV (<http://therp.nl>).
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
from openerp.tools.translate import _
from openerp.addons.decimal_precision import decimal_precision as dp


class instant_voucher(orm.TransientModel):
    _name = 'account.voucher.instant'
    _description = 'Instant Voucher'

    def cancel(self, cr, uid, ids, context=None):
        """
        Delete the voucher and close window
        """
        assert len(ids) == 1, "Will only take one resource id"
        instant = self.browse(cr, uid, ids[0], context=context)
        if instant.voucher_id:
            self.pool.get('account.voucher').cancel_voucher(
                cr, uid, [instant.voucher_id.id], context=context)
            self.pool.get('account.voucher').unlink(
                cr, uid, [instant.voucher_id.id], context=context)
        return {'type': 'ir.actions.act_window_close'}

    def get_voucher_defaults(self, cr, uid, vals, context=None):
        """
        Gather conditional defaults based on given key, value pairs

        :param vals: dictionary of key, value pairs
        :returns: dictionary of default values for fields not in vals
        """
        values_pool = self.pool.get('ir.values')
        voucher_pool = self.pool.get('account.voucher')
        res = {}
        for (key, val) in vals.iteritems():
            if val and voucher_pool._all_columns[key].column.change_default:
                for default in values_pool.get_defaults(
                        cr, uid, 'account.voucher', '%s=%s' % (key, val)):
                    if default[1] not in vals:
                        res[default[1]] = default[2]
        return res

    def create_voucher(self, cr, uid, ids, context=None):
        """
        Create a fully fledged voucher counterpart for the
        statement line. User only needs to process taxes and may
        adapt cost/income account.
        """
        assert len(ids) == 1, "Will only take one resource id"
        voucher_pool = self.pool.get('account.voucher')
        period_pool = self.pool.get('account.period')
        instant = self.browse(cr, uid, ids[0], context=context)
        line = instant.statement_line_id
        voucher_type = line.amount < 0 and 'purchase' or 'sale'
        journal_ids = self.pool.get('account.journal').search(
            cr, uid, [('company_id', '=', line.company_id.id),
                      ('type', '=', voucher_type)])
        if not journal_ids:
            orm.exept_orm(
                _('Error'),
                _('No %s journal defined') % voucher_type)

        journal = self.pool.get('account.journal').browse(
            cr, uid, journal_ids[0], context=context)
        if journal.type in ('sale', 'sale_refund'):
            line_account_id = (
                journal.default_credit_account_id and
                journal.default_credit_account_id.id or False
            )
        elif journal.type in ('purchase', 'expense', 'purchase_refund'):
            line_account_id = (
                journal.default_debit_account_id and
                journal.default_debit_account_id.id or False
            )
        vals = {
            'name': (_('Voucher for statement line %s.%s') %
                     (line.statement_id.name, line.name)),
            'reference': line.ref or False,
            'company_id': line.company_id.id,
            'partner_id': instant.partner_id.id,
            'date': line.date or False,
            'account_id': line.account_id.id,
            'type': voucher_type,
            'line_ids': [(0, 0, {'amount': abs(line.amount),
                                 'account_id': line_account_id,
                                 'type': line.amount < 0 and 'dr' or 'cr',
                                 'name': line.ref or False,
                                 })],
            'amount': line.amount and abs(line.amount) or False,
            'journal_id': journal_ids[0],
        }
        if vals['date']:
            period_ids = period_pool.find(
                cr, uid, vals['date'], context=context
            )
            if period_ids:
                vals['period_id'] = period_ids[0]
        vals.update(self.get_voucher_defaults(cr, uid, vals, context=context))

        voucher_id = voucher_pool.create(
            cr, uid, vals, context=context)
        self.write(
            cr, uid, ids[0],
            {'voucher_id': voucher_id,
             'state': 'ready',
             'type': voucher_type,
             }, context=context)
        return {
            'name': self._description,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'domain': [],
            'context': context,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': ids[0],
            'nodestroy': False,
        }

    def dummy(self, cr, uid, ids, context=None):
        return {
            'name': self._description,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'domain': [],
            'context': context,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': ids[0],
            'nodestroy': False,
        }

    def default_get(self, cr, uid, fields_list, context=None):
        """
        Gather sane default values from the originating statement line
        """
        res = super(instant_voucher, self).default_get(
            cr, uid, fields_list, context=context)
        if 'statement_line_id' in fields_list:
            res['statement_line_id'] = (
                context.get('active_id') or
                context.get('active_ids') and context.get('active_ids')[0])
            if not res['statement_line_id']:
                raise orm.except_orm(
                    _('Error'),
                    _('Cannot determine statement line'))
            line = self.pool.get('account.bank.statement.line').browse(
                cr, uid, res['statement_line_id'], context=context)
            if 'balance' in fields_list:
                res['balance'] = line.amount
            if 'ref' in fields_list:
                res['ref'] = line.ref
            if 'partner_id' in fields_list:
                if line.partner_id:
                    res['partner_id'] = line.partner_id.id
        return res

    def _get_balance(self, cr, uid, ids, field_name, args, context=None):
        """
        Compute the expected residual
        TODO: currency conversion
        """
        res = {}
        for instant in self.browse(cr, uid, ids, context=context):
            if instant.voucher_id and instant.voucher_id.state == 'posted':
                amount = instant.statement_line_id.amount
                counteramount = 0.0
                statement_account_id = instant.statement_line_id.account_id.id
                for line in instant.voucher_id.move_ids:
                    if line.account_id.id == statement_account_id:
                        counteramount = line.debit - line.credit
                for line in instant.voucher_id.move_ids:
                    if line.account_id.id == statement_account_id:
                        counteramount = line.debit - line.credit
            else:
                amount = abs(instant.statement_line_id.amount)
                counteramount = abs(instant.voucher_id and
                                    instant.voucher_id.amount or 0.0)
            res[instant.id] = amount - counteramount
        return res

    def confirm(self, cr, uid, ids, context=None):
        """
        Post the voucher if necessary
        Post the voucher's move lines if necessary
        Sanity checks on currency and residual = 0.0

        If the account_banking module is installed, perform matching
        and reconciliation. If not, the user is left to manual
        reconciliation of OpenERP.
        """
        assert len(ids) == 1, "Will only take one resource id"
        statement_line_obj = self.pool.get('account.bank.statement.line')
        voucher_obj = self.pool.get('account.voucher')
        move_obj = self.pool.get('account.move')
        instant = self.browse(cr, uid, ids[0], context=context)
        statement_line = instant.statement_line_id
        voucher_currency = (instant.voucher_id.currency_id and
                            instant.voucher_id.currency_id or
                            instant.voucher_id.company_id.currency_id)
        if (statement_line.statement_id.currency.id != voucher_currency.id):
            raise orm.except_orm(
                _("Error"),
                _("Currency on the bank statement line needs to be the "
                  "same as on the voucher. Currency conversion is not yet "
                  "supported."))
        if instant.voucher_id.state != 'posted':
            voucher_obj.proforma_voucher(
                cr, uid, [instant.voucher_id.id], context=context)
            instant.refresh()
            if instant.voucher_id.state != 'posted':
                raise orm.except_orm(
                    _("Error"),
                    _("The voucher could not be posted."))
        if instant.voucher_id.move_id.state != 'posted':
            move_obj.post(
                cr, uid, [instant.voucher_id.move_id.id], context=context)
            instant.refresh()
            if instant.voucher_id.move_id.state != 'posted':
                raise orm.except_orm(
                    _("Error"),
                    _("The voucher's move line could not be posted."))
        if not self.pool.get('res.currency').is_zero(
                cr, uid, voucher_currency, instant.balance):
            raise orm.except_orm(
                _("Error"),
                _("The amount on the bank statement line needs to be the "
                  "same as on the voucher. Write-off is not yet "
                  "supported."))
        # Banking Addons integration:
        # Gather the info needed to match the bank statement line
        # and trigger its posting and reconciliation.
        if 'import_transaction_id' in statement_line_obj._columns:
            if instant.statement_line_id.state == 'confirmed':
                raise orm.except_orm(
                    _("Error"),
                    _("Cannot match a confirmed statement line"))
            if not statement_line.import_transaction_id:
                statement_line_obj.create_instant_transaction(
                    cr, uid, statement_line.id, context=context)
                statement_line.refresh()
            for line in instant.voucher_id.move_ids:
                if line.account_id.id == statement_line.account_id.id:
                    self.pool.get('banking.import.transaction').write(
                        cr,
                        uid,
                        statement_line.import_transaction_id.id,
                        {
                            'move_line_id': line.id,
                            'move_line_ids': [(6, 0, [line.id])],
                            'match_type': 'move',
                            'invoice_id': False,
                            'invoice_ids': [(6, 0, [])],
                        },
                        context=context
                    )

                    statement_line_obj.confirm(
                        cr, uid, [statement_line.id], context=context
                    )
                    break
        return {'type': 'ir.actions.act_window_close'}

    _columns = {
        'balance': fields.function(
            _get_balance,
            type='float',
            digits_compute=dp.get_precision('Account'),
            string="Balance",),
        'partner_id': fields.many2one(
            'res.partner',
            'Partner',
            required=True),
        'statement_line_id': fields.many2one(
            'account.bank.statement.line',
            'Bank statement line',
            readonly=True),
        'ref': fields.related(
            'statement_line_id', 'ref',
            type="char", size="48",
            readonly=True,
            string="Reference"),
        'voucher_id': fields.many2one(
            'account.voucher',
            'Voucher',
            readonly=True),
        'state': fields.selection(
            [('init', 'init'),
             ('ready', 'ready'),
             ('confirm', 'confirm')],
            'State'),
        'type': fields.selection(
            [('sale', 'Sale'),
             ('purchase', 'Purchase')],
            'Voucher type'),
    }

    _defaults = {'state': 'init'}
