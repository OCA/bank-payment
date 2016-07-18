# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models, tools


class PaymentOrderCreate(models.TransientModel):
    _inherit = 'payment.order.create'

    @api.multi
    def create_payment(self):
        result = super(PaymentOrderCreate, self).create_payment()
        mandate2amount = {}
        payment_order = self.env['payment.order'].browse(
            self.env.context['active_id'])
        for payment_line in payment_order.line_ids:
            mandate = payment_line.mandate_id
            if not mandate.max_amount_per_date:
                continue
            mandate2amount.setdefault(mandate, 0)
            max_amount = self._get_max_amount(payment_order, mandate)
            if tools.float_compare(
                mandate2amount[mandate] + payment_line.amount,
                max_amount,
                precision_digits=mandate._fields['max_amount_per_date']
                .digits[1],
            ) == 1:
                payment_line.write({
                    'amount_currency': payment_line.company_currency.compute(
                        max_amount - mandate2amount[mandate],
                        payment_line.currency,
                    ),
                })
                if not payment_line.amount:
                    payment_line.unlink()
                    continue
            mandate2amount[mandate] += payment_line.amount
        # trigger recomputation of total
        payment_order.write({'line_ids': []})
        return result

    @api.model
    def _get_max_amount(self, payment_order, mandate):
        """return the maximum amount the mandate allows to put on the payment
        order"""
        date_start = fields.Datetime.from_string(
            mandate.last_debit_date) or mandate.rrule[:1][0]
        date_end = fields.Datetime.from_string(
            payment_order.date_scheduled or fields.Datetime.now())
        return mandate.max_amount_per_date * len(
            list(mandate.rrule.between(date_start, date_end, inc=True)))
