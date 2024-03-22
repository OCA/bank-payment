# © 2022 Acsone (<http://www.acsone.eu>))
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountPaymentOrder(models.Model):

    _inherit = "account.payment.order"

    name = fields.Char(
        compute="_compute_name",
        store=True,
    )

    @api.depends("payment_mode_id.sequence_payment_order_id")
    def _compute_name(self):
        # do not increment sequence when computing on new id
        for rec in self.filtered("id"):
            if rec.payment_mode_id and rec.payment_mode_id.sequence_payment_order_id:
                rec.name = rec.payment_mode_id.sequence_payment_order_id._next()
            else:
                rec.name = (
                    self.env["ir.sequence"].next_by_code("account.payment.order")
                    or "New"
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                # Put val in name to avoid computation of sequence in create
                # It was done in module account_payment_order
                vals["name"] = "TMP"

        return super().create(vals_list)
