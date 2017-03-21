# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import _, api, fields, models, tools


class PaymentOrderCreate(models.TransientModel):
    _inherit = 'payment.order.create'

    @api.multi
    def create_payment(self):
        result = super(PaymentOrderCreate, self).create_payment()
        mandate2amount = {}
        payment_order = self.env['payment.order'].browse(
            self.env.context['active_id'])
        messages = ''
        for payment_line in payment_order.line_ids.sorted(
            lambda x: x.date, reverse=True
        ):
            mandate = payment_line.mandate_id
            if not mandate.max_amount_per_date:
                messages += '<div>' + _(
                    "Ignoring mandate %s because it doesn't set a maximum to "
                    "invoice "
                ) % (
                    mandate.display_name
                ) + '</div>'
                continue
            mandate2amount.setdefault(mandate, 0)
            date_start, date_end, max_amount = self._get_mandate_parameters(
                payment_order, mandate
            )
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
                messages += '<div>' + _(
                    'Capping %s to %s: Mandate has %s occurrences between '
                    '%s and %s, totalling to %d for this run'
                ) % (
                    payment_line.ml_inv_ref.display_name, payment_line.amount,
                    len(mandate.rrule.between(date_start, date_end, inc=True)),
                    date_start, date_end, max_amount
                ) + '</div>'
                if not payment_line.amount:
                    payment_line.unlink()
                    continue
            else:
                messages += '<div>' + _(
                    'Not capping %s (%d): Mandate has %s occurrences between '
                    '%s and %s, totalling to %d for this run'
                ) % (
                    payment_line.ml_inv_ref.display_name, payment_line.amount,
                    len(mandate.rrule.between(date_start, date_end, inc=True)),
                    date_start, date_end, max_amount,
                ) + '</div>'
            mandate2amount[mandate] += payment_line.amount
        # trigger recomputation of total
        payment_order.write({
            'line_ids': [],
            'restrict_mandate_messages': messages or False,
        })
        return result

    @api.model
    def _get_mandate_parameters(self, payment_order, mandate):
        """return the maximum amount the mandate allows to put on the payment
        order"""
        date_start = fields.Datetime.from_string(
            mandate.last_debit_date) or mandate.rrule[:1][0]
        date_end = fields.Datetime.from_string(
            payment_order.date_scheduled or fields.Datetime.now())
        return date_start, date_end, mandate.max_amount_per_date * len(
            list(mandate.rrule.between(date_start, date_end, inc=True)))
