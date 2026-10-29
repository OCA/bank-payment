# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    payment_schedule_minimum_balance = fields.Monetary(
        related="company_id.payment_schedule_minimum_balance",
        currency_field="currency_id",
        readonly=False,
    )
