# Copyright 2009-2023 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountPaymentUpdate(models.TransientModel):
    _name = "account.payment.update"
    _description = "Update Payment Reference"

    payment_reference = fields.Char(required=True)

    def update_payment_reference(self):
        payment = self.env["account.payment"].browse(self.env.context.get("active_id"))
        payment.payment_reference = self.payment_reference
        payment.ref = self.payment_reference
