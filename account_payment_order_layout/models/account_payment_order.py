# Copyright 2023 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    def generate_payment_file(self):
        if not self.payment_mode_id.layout_id:
            return super().generate_payment_file()
        return self.payment_mode_id.layout_id.generate_payment_file(self)
