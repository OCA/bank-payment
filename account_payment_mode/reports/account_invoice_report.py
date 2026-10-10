# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    payment_mode_id = fields.Many2one(
        comodel_name="account.payment.mode",
        string="Payment mode",
        readonly=True,
    )

    def _select_list(self, table):
        return super()._select_list(table) + [table.move_id.payment_mode_id]
