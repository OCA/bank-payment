# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    payment_schedule_minimum_balance = fields.Monetary(
        string="Minimum Balance",
        currency_field="currency_id",
        help="The payment schedule warns about the dates whose projected balance "
        "is below this amount.",
    )
