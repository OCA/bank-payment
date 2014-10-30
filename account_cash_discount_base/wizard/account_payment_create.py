# -*- coding: utf-8 -*-
#
##############################################################################
#
#    Authors: Adrien Peiffer
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
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

from openerp import models, api, fields
from openerp.tools.translate import _
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class PaymentOrderCreate(models.TransientModel):
    _inherit = 'payment.order.create'

    cash_discount_date = fields.Boolean(string="Cash Discount Due Date",
                                        default=False)

    def _prepare_payment_line(self, payment, line):
        res = super(PaymentOrderCreate, self)._prepare_payment_line(payment,
                                                                    line)
        move_line_obj = self.env['account.move.line']
        res.update({'base_amount': res['amount_currency']})
        if res['move_line_id']:
            move_line = move_line_obj.browse([res['move_line_id']])
            today = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
            if move_line.invoice and move_line.invoice.discount_due_date:
                invoice = move_line.invoice
                if invoice.discount_due_date >= today and \
                        invoice.amount_total == line.amount_residual:
                    amount_currency = invoice.amount_total - \
                        invoice.discount_amount
                    res.update({'amount_currency': amount_currency,
                                'discount_amount': invoice.discount_amount})
        return res

    @api.multi
    def search_entries(self):
        if not self.cash_discount_date:
            return super(PaymentOrderCreate, self).search_entries()
        line_obj = self.env['account.move.line']
        model_data_obj = self.env['ir.model.data']
        # -- start account_banking_payment --
        payment = self.env['payment.order'].browse(
            self.env.context['active_id'])
        # Search for move line to pay:
        domain = [('move_id.state', '=', 'posted'),
                  ('reconcile_id', '=', False),
                  ('company_id', '=', payment.mode.company_id.id)]
        self.extend_payment_order_domain(payment, domain)
        # -- end account_direct_debit --
        domain += [('invoice.discount_due_date', '<=', self.duedate)]
        lines = line_obj.search(domain)
        context = self.env.context.copy()
        context['line_ids'] = lines.ids
        context['populate_results'] = self.populate_results
        model_datas = model_data_obj.search(
            [('model', '=', 'ir.ui.view'),
             ('name', '=', 'view_create_payment_order_lines')])
        return {'name': _('Entry Lines'),
                'context': context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'payment.order.create',
                'views': [(model_datas[0].res_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
                }
