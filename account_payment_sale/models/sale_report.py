# Copyright 2021-2022 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    payment_mode_id = fields.Many2one(
        "account.payment.mode",
        string="Payment Mode",
        readonly=True,
    )

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res["payment_mode_id"] = "s.payment_mode_id"
        return res
