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
import time

from openerp.osv import fields, osv

class account_statement_from_invoice_lines(osv.osv_memory):
    """
    Generate Entries by Statement from Invoices
    """
    _inherit = "account.statement.from.invoice.lines"


    def populate_statement(self, cr, uid, ids, context=None):
        context = dict(context or {})
        statement_id = context.get('statement_id', False)
        if not statement_id:
            return {'type': 'ir.actions.act_window_close'}
        data = self.read(cr, uid, ids, context=context)[0]
        line_ids = data['line_ids']
        if not line_ids:
            return {'type': 'ir.actions.act_window_close'}

        line_obj = self.pool.get('account.move.line')
        statement_obj = self.pool.get('account.bank.statement')
        statement_line_obj = self.pool.get('account.bank.statement.line')
        currency_obj = self.pool.get('res.currency')
        statement = statement_obj.browse(cr, uid, statement_id, context=context)
        line_date = statement.date

        # for each selected move lines
        for line in line_obj.browse(cr, uid, line_ids, context=context):
            ctx = context.copy()
            #  take the date for computation of currency => use payment date
            ctx['date'] = line_date
            amount = 0.0
            amount_currency = 0.0
            if line.invoice and line.invoice.currency_id == statement.currency_id:
                amount = line.amount_residual_currency
                amount_currency = 0.0
            else:
                amount = 0.0
                amount_currency = line.amount_residual_currency

            context.update({'move_line_ids': [line.id],
                            'invoice_id': line.invoice.id})

            statement_line_obj.create(cr, uid, {
                'name': line.name or '?',
                'amount': amount,
                'partner_id': line.partner_id.id,
                'statement_id': statement_id,
                'ref': line.ref,
                'date': statement.date,
                'amount_currency': amount_currency,
                'currency_id': line.currency_id.id,
            }, context=context)
        return {'type': 'ir.actions.act_window_close'}
