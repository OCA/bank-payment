# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountPaymentMethod(models.Model):
    _inherit = "account.payment.method"

    payment_order_ok = fields.Boolean(
        string="Payment Orders",
        help="Check this option for payment methods designed to be used "
        "in payment orders.",
    )
