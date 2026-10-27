# Copyright 2025 ForgeFlow
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    mandate_id = fields.Many2one(
        "account.banking.mandate", compute="_compute_mandate_id"
    )

    @api.depends(
        "payment_line_ids.mandate_id",
        "move_id.mandate_id",
    )
    def _compute_mandate_id(self):
        for payment in self:
            payment.mandate_id = (
                payment.move_id.mandate_id or payment.payment_line_ids[:1].mandate_id
            )
