# Copyright 2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    grouped_payment_order_id = fields.Many2one(
        comodel_name="account.payment.order",
        string="Payment Order (Grouped)",
        copy=False,
        readonly=True,
        check_company=True,
    )
