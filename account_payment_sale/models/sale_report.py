# Copyright 2021-2022 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    payment_mode_id = fields.Many2one(
        "account.payment.mode",
        readonly=True,
    )

    def _select_dict(self, table):
        return super()._select_dict(table) | {
            "payment_mode_id": table.order_id.payment_mode_id
        }
