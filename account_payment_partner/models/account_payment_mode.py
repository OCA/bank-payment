# Copyright 2017 ForgeFlow S.L.
# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AccountPaymentMode(models.Model):
    _inherit = "account.payment.mode"

    show_bank_account = fields.Selection(
        selection=[
            ("full", "Full"),
            ("first", "First n chars"),
            ("last", "Last n chars"),
            ("first_last", "First n chars and Last n chars"),
            ("no", "No"),
        ],
        default="full",
        help="Show in invoices partial or full bank account number",
    )
    show_bank_account_chars = fields.Integer(
        string="# of digits for customer bank account",
        default=4,
    )
    refund_payment_mode_id = fields.Many2one(
        comodel_name="account.payment.mode",
        domain="[('payment_type', '!=', payment_type)]",
        string="Payment mode for refunds",
        help="This payment mode will be used when doing "
        "refunds coming from the current payment mode.",
        check_company=True,
    )

    _sql_constraints = [
        (
            "show_bank_account_chars_positive",
            "CHECK(show_bank_account_chars >= 0)",
            "The number of digits for customer bank account must be positive or null.",
        )
    ]
