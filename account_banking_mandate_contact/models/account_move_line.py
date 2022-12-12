# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # Extended to use partner_shipping_id mandate if it have set
    def _prepare_payment_line_vals(self, payment_order):
        vals = super(AccountMoveLine, self)._prepare_payment_line_vals(payment_order)
        if payment_order.payment_type != "inbound" or self.move_id.mandate_id:
            return vals
        mandate = (
            self.move_id.partner_shipping_id.valid_mandate_id
            or self.move_id.partner_id.valid_mandate_id
        )
        if mandate:
            vals.update(
                {
                    "mandate_id": mandate.id,
                    "partner_bank_id": mandate.partner_bank_id.id,
                }
            )
        return vals
