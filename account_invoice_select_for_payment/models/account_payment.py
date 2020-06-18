# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def action_register_payment(self):
        active_ids = self.env.context.get("active_ids")
        if active_ids:
            invoices = self.env["account.move"].search(
                [("id", "in", active_ids), ("selected_for_payment", "=", True)]
            )
            invoices.write({"selected_for_payment": False})
        return super().action_register_payment()
