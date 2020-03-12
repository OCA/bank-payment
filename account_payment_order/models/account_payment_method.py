# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountPaymentMethod(models.Model):
    _inherit = "account.payment.method"

    payment_order_only = fields.Boolean(
        string="Only for payment orders",
        help="This option helps enforcing the use of payment orders for "
        "some payment methods.",
        default=False,
    )
