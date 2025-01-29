# Copyright 2020 Marçal Isern <marsal.isern@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    mandate_id = fields.Many2one(
        "account.banking.mandate",
        string="Direct Debit Mandate",
        ondelete="restrict",
        check_company=True,
        compute="_compute_mandate_id",
        readonly=False,
        store=True,
    )
    mandate_required = fields.Boolean(
        related="preferred_payment_method_line_id.payment_method_id.mandate_required"
    )

    @api.depends("preferred_payment_method_line_id", "company_id", "partner_id")
    def _compute_mandate_id(self):
        for move in self:
            if move.preferred_payment_method_line_id.payment_method_id.mandate_required:
                move = move.with_company(move.company_id.id)
                move.mandate_id = move.partner_id.valid_mandate_id
            else:
                move.mandate_id = False
