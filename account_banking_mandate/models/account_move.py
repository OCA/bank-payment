# Copyright 2020-2022 Marçal Isern <marsal.isern@qubiq.es>
# Copyright 2022 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    mandate_id = fields.Many2one(
        "account.banking.mandate",
        compute="_compute_mandate_id",
        string="Direct Debit Mandate",
        ondelete="restrict",
        check_company=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    mandate_required = fields.Boolean(
        related="payment_mode_id.payment_method_id.mandate_required", readonly=True
    )

    @api.depends("commercial_partner_id", "company_id", "payment_mode_id")
    def _compute_mandate_id(self):
        for move in self:
            if move.payment_mode_id.payment_method_id.mandate_required:
                move.mandate_id = move.commercial_partner_id.valid_mandate_id
            else:
                move.mandate_id = False
