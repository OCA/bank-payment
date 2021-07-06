# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class AccounttMove(models.Model):
    _inherit = "account.move"

    alllow_payment_mode_id_filter_domain = fields.Many2many(
        comodel_name="account.payment.mode",
        compute="_compute_alllow_payment_mode_id_filter_domain",
        store=False,
    )

    @api.depends("invoice_payment_term_id", "payment_mode_id")
    def _compute_alllow_payment_mode_id_filter_domain(self):
        for move in self:
            move.alllow_payment_mode_id_filter_domain = False
            if move.invoice_payment_term_id:
                term = move.invoice_payment_term_id
                move.alllow_payment_mode_id_filter_domain = term.payment_mode_ids
            elif move.payment_mode_id:
                move.alllow_payment_mode_id_filter_domain = [
                    [6, 0, [move.payment_mode_id.id]]
                ]
