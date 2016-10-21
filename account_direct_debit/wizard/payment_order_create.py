# -*- coding: utf-8 -*-
# © 2013 Therp BV (<http://therp.nl>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class PaymentOrderCreate(models.TransientModel):
    _inherit = 'payment.order.create'

    @api.multi
    def extend_payment_order_domain(self, payment_order, domain):
        super(PaymentOrderCreate, self).extend_payment_order_domain(
            payment_order, domain)
        if payment_order.payment_order_type == 'debit':
            # For receivables, propose all unreconciled debit lines,
            # including partially reconciled ones.
            # If they are partially reconciled with a customer refund,
            # the residual will be added to the payment order.
            #
            # For payables, normally suppliers will be the initiating party
            # for possible supplier refunds (via a transfer for example),
            # or they keep the amount for decreasing future supplier invoices,
            # so there's not too much sense for adding them to a direct debit
            # order
            domain += [
                ('debit', '>', 0),
                ('account_id.type', '=', 'receivable'),
            ]
        return True
