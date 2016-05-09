# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 - 2013 Therp BV (<http://therp.nl>).
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

from openerp.osv import orm
from openerp.tools import ustr


class AccountBankStatement(orm.Model):
    _inherit = 'account.bank.statement'

    def get_tax_move_lines(
            self, cr, uid, st_line, defaults,
            company_currency_id, context=None):
        """
        Process inclusive taxes on bank statement lines.

        @param st_line: browse record of the statement line
        @param defaults: dictionary of default move line values. Usually
        the same as the originating move line.

        return one or more serialized tax move lines and a set of values to
        update the originating move line with, containing the new amount.
        """

        if not st_line.tax_id:
            return False, False
        tax_obj = self.pool.get('account.tax')
        move_lines = []
        update_move_line = {}
        base_amount = -defaults['credit'] or defaults['debit']
        tax_obj = self.pool.get('account.tax')

        fiscal_position = (
            st_line.partner_id.property_account_position
            if (st_line.partner_id and
                st_line.partner_id.property_account_position)
            else False)
        tax_ids = self.pool.get('account.fiscal.position').map_tax(
            cr, uid, fiscal_position, [st_line.tax_id])
        taxes = tax_obj.browse(cr, uid, tax_ids, context=context)

        computed_taxes = tax_obj.compute_all(
            cr, uid, taxes, base_amount, 1.00)

        for tax in computed_taxes['taxes']:
            if tax['tax_code_id']:
                if not update_move_line.get('tax_code_id'):
                    update_move_line['tax_code_id'] = tax['base_code_id']
                    update_move_line['tax_amount'] = tax['base_sign'] * (
                        computed_taxes.get('total', 0.0))
                    # As the tax is inclusive, we need to correct the amount
                    # on the original move line
                    amount = computed_taxes.get('total', 0.0)
                    update_move_line['credit'] = (
                        (amount < 0) and -amount) or 0.0
                    update_move_line['debit'] = (
                        (amount > 0) and amount) or 0.0

                move_lines.append({
                    'move_id': defaults['move_id'],
                    'name': (
                        defaults.get('name', '') + ' ' +
                        ustr(tax['name'] or '')),
                    'date': defaults.get('date', False),
                    'partner_id': defaults.get('partner_id', False),
                    'ref': defaults.get('ref', False),
                    'statement_id': defaults.get('statement_id'),
                    'tax_code_id': tax['tax_code_id'],
                    'tax_amount': tax['tax_sign'] * tax.get('amount', 0.0),
                    'account_id': (
                        tax.get('account_collected_id',
                                defaults['account_id'])),
                    'credit': tax['amount'] < 0 and - tax['amount'] or 0.0,
                    'debit': tax['amount'] > 0 and tax['amount'] or 0.0,
                })

        return move_lines, update_move_line

    def _prepare_bank_move_line(
            self, cr, uid, st_line, move_id, amount, company_currency_id,
            context=None):
        """
        Overload of the original method from the account module. Create
        the tax move lines.
        """
        res = super(AccountBankStatement, self)._prepare_bank_move_line(
            cr, uid, st_line, move_id, amount, company_currency_id,
            context=context)
        if st_line.tax_id:
            tax_move_lines, counterpart_update_vals = self.get_tax_move_lines(
                cr, uid, st_line, res, company_currency_id, context=context)
            res.update(counterpart_update_vals)
            for tax_move_line in tax_move_lines:
                self.pool.get('account.move.line').create(
                    cr, uid, tax_move_line, context=context)
        return res
