# Copyright 2016 Akretion (http://www.akretion.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    payment_mode_id = fields.Many2one(
        comodel_name="account.payment.mode",
        compute="_compute_payment_mode",
        store=True,
        ondelete="restrict",
        index=True,
        readonly=False,
    )

    @api.depends("move_id", "move_id.payment_mode_id")
    def _compute_payment_mode(self):
        for line in self:
            if line.move_id.is_invoice() and line.account_type in (
                "asset_receivable",
                "liability_payable",
            ):
                line.payment_mode_id = line.move_id.payment_mode_id
            else:
                line.payment_mode_id = False

    def write(self, vals):
        """Propagate up to the move the payment mode if applies."""
        if "payment_mode_id" in vals:
            for record in self:
                move = (
                    self.env["account.move"].browse(vals.get("move_id", 0))
                    or record.move_id
                )
                if (
                    move.payment_mode_id.id != vals["payment_mode_id"]
                    and move.is_invoice()
                ):
                    move.payment_mode_id = vals["payment_mode_id"]
        return super().write(vals)
