# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PaymentToken(models.Model):
    _inherit = 'payment.token'

    def _compute_is_default_payment(self):
        for token in self:
            is_default = token.partner_id.payment_token_id == token
            token.is_default_payment = is_default

    is_default_payment = fields.Boolean(
        "Is Default Payment",
        compute=_compute_is_default_payment,
        readonly=True,
    )

    def set_default_payment(self):
        self.ensure_one()
        self.partner_id.payment_token_id = self
