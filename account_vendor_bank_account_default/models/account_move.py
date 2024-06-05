# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _compute_partner_bank_id(self):
        res = super()._compute_partner_bank_id()
        for move in self:
            payment_mode = move.payment_mode_id
            if (
                payment_mode
                and move.move_type == "in_invoice"
                and payment_mode.payment_type == "outbound"
                and payment_mode.payment_method_id.bank_account_required
            ):
                move.partner_bank_id = (
                    move.bank_partner_id.default_bank_id
                    if move.bank_partner_id.has_default_bank_id
                    else False
                )
        return res
