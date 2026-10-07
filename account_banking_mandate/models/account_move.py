# Copyright 2020 Marçal Isern <marsal.isern@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    mandate_id = fields.Many2one(
        "account.banking.mandate",
        string="Direct Debit Mandate",
        ondelete="restrict",
        readonly=False,
        check_company=True,
        compute="_compute_mandate_id",
        store="True",
    )
    mandate_required = fields.Boolean(
        related="payment_mode_id.payment_method_id.mandate_required", readonly=True
    )

    @api.depends("company_id", "payment_mode_id", "partner_id")
    def _compute_mandate_id(self):
        for move in self:
            move = move.with_company(move.company_id)
            if move.payment_mode_id.payment_method_id.mandate_required:
                move.mandate_id = move.partner_id.valid_mandate_id
            else:
                move.mandate_id = False

    def partner_banks_to_show(self):
        res = super().partner_banks_to_show()
        if (
            not res
            and self.payment_mode_id.payment_method_id.code == "sepa_direct_debit"
        ):  # pragma: no cover
            return (
                self.mandate_id.partner_bank_id
                or self.partner_id.valid_mandate_id.partner_bank_id
            )
        return res
