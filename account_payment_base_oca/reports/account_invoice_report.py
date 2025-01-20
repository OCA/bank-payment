# Copyright 2024-2025 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import SQL


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    payment_method_line_id = fields.Many2one(
        "account.payment.method.line", readonly=True, string="Payment Mode"
    )

    @api.model
    def _select(self) -> SQL:
        return SQL(
            "%s, move.preferred_payment_method_line_id AS " "payment_method_line_id",
            super()._select(),
        )
