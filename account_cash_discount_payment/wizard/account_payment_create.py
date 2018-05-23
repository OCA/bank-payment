# -*- coding: utf-8 -*-
#
##############################################################################
#
#    Authors: Adrien Peiffer
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
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


class PaymentOrderCreate(models.TransientModel):
    _inherit = 'payment.order.create'

    cash_discount_date = fields.Boolean(string="Cash Discount Due Date",
                                        default=False)
    cash_discount_date_start = fields.Date(string="Cash discount Start Date")
    cash_discount_date_end = fields.Date(string="Cash discount End Date")

    def _prepare_payment_line(self, payment, line):
        res = super(PaymentOrderCreate, self)._prepare_payment_line(payment,
                                                                    line)
        move_line_obj = self.env['account.move.line']
        res.update({'base_amount': res['amount_currency']})
        if res['move_line_id']:
            move_line = move_line_obj.browse([res['move_line_id']])
            today = fields.Date.today()
            if move_line.invoice and move_line.invoice.discount_due_date:
                invoice = move_line.invoice
                if invoice.discount_due_date >= today:
                    discount = invoice.amount_total - \
                        invoice.discount_amount
                    amount_discount = line.amount_residual - discount
                    res.update({'amount_currency': amount_discount,
                                'discount_amount': discount})
        return res

    @api.model
    def extend_payment_order_domain(self, payment_order, domain):
        # TODO : Improvement to remove partial domain (while loop)
        context = self.env.context
        super(PaymentOrderCreate, self)\
            .extend_payment_order_domain(payment_order, domain)
        if context.get('cash_discount_date', False) and \
                context.get('due_date', False):
            due_date = context.get('due_date', False)
            date_start = context.get('date_start', False)
            date_end = context.get('date_end', False)
            pos = 0
            while pos < len(domain):
                if pos < len(domain)-2 and domain[pos] == '|' and \
                        domain[pos+1] == ('date_maturity', '<=',
                                          due_date) \
                        and domain[pos+2] == ('date_maturity', '=', False):
                    domain.pop(pos)
                    domain.pop(pos)
                    domain.pop(pos)
                    break
                pos += 1
            domain += [('invoice.discount_due_date', '>=', date_start),
                       ('invoice.discount_due_date', '<=', date_end)]
        return True

    @api.multi
    def search_entries(self):
        ctx = self.env.context.copy()
        if self.cash_discount_date:
            ctx.update({'cash_discount_date': True,
                        'due_date': self.duedate,
                        'date_start': self.cash_discount_date_start,
                        'date_end': self.cash_discount_date_end})
        else:
            ctx.update({'cash_discount_date': False})
        return super(PaymentOrderCreate, self.with_context(ctx))\
            .search_entries()
