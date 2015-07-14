# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Vincent Renaville (Camptocamp)
#    Copyright 2015 Camptocamp SA
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
from openerp import models, api


class account_statement_from_invoice_lines(models.TransientModel):
    """
    Generate Entries by Statement from Invoices
    """
    _inherit = "account.statement.from.invoice.lines"

    @api.multi
    def populate_statement(self):
        statement_id = self.env.context.get('statement_id', False)
        if not statement_id or not self.line_ids:
            return {'type': 'ir.actions.act_window_close'}

        statement_obj = self.env['account.bank.statement']
        statement_line_obj = self.env['account.bank.statement.line']
        statement = statement_obj.browse(statement_id)
        line_date = statement.date
        # Get the currency on the company if not set on the journal
        if statement.journal_id.currency:
            from_currency_id = statement.journal_id.currency
        else:
            from_currency_id = self.env.user.company_id.currency_id

        # for each selected move lines
        for line in self.line_ids:
            if line.invoice and line.invoice.currency_id == from_currency_id:
                amount = line.amount_residual_currency
                amount_currency = 0.0
            else:
                if statement.journal_id.currency:
                    from_currency_id = statement.journal_id.currency
                else:
                    from_currency_id = self.env.user.company_id.currency_id
                amount = from_currency_id.with_context(date=line_date).compute(
                    line.amount_residual_currency,
                    line.invoice.currency_id)
                amount_currency = line.amount_residual_currency
            # we test how to apply sign
            if line.journal_id.type in ['sale_refund', 'purchase']:
                amount_currency = -amount_currency
                amount = -amount
            ctx = {}
            ctx.update({'move_line_ids': [line.id],
                        'invoice_id': line.invoice.id})

            statement_line_obj.with_context(ctx).create({
                'name': line.name or '?',
                'amount': amount,
                'partner_id': line.partner_id.id,
                'statement_id': statement_id,
                'ref': line.ref,
                'date': statement.date,
                'amount_currency': amount_currency,
                'currency_id': line.currency_id.id,
            })
        return {'type': 'ir.actions.act_window_close'}
