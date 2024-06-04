# Copyright 2024 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    # Extended to use partner_shipping_id mandate if it have set
    def partner_banks_to_show(self):
        if (
            not self.partner_bank_id
            and self.payment_mode_id.payment_method_id.code == "sepa_direct_debit"
            and self.partner_shipping_id.valid_mandate_id
        ):
            return self.partner_shipping_id.valid_mandate_id.partner_bank_id
        else:
            return super().partner_banks_to_show()
