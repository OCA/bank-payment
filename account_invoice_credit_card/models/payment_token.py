# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PaymentToken(models.Model):
    _inherit = 'payment.token'

    is_default_payment = fields.Boolean("Is Default Payment")

    def set_default_payment(self):
        self.is_default_payment = True
        self.partner_id.payment_token_id = self.id or self.origin.id
