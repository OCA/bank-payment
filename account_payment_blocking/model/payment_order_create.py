# -*- coding: utf-8 -*-
# Copyright 2014-2015 ACSONE SA/NV (http://acsone.eu)
# Author: Stéphane Bidoul <stephane.bidoul@acsone.eu>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class PaymentOrderCreate(models.TransientModel):
    _inherit = 'payment.order.create'

    @api.multi
    def extend_payment_order_domain(
            self, payment_order, domain):
        super(PaymentOrderCreate, self).extend_payment_order_domain(
            payment_order, domain)
        domain += [('blocked', '!=', True)]
        return True
