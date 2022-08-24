# © 2022 Acsone (<http://www.acsone.eu>))
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountPaymentMode(models.Model):

    _inherit = "account.payment.mode"

    sequence_payment_order_id = fields.Many2one(
        "ir.sequence",
        string="Sequence for payment order",
        domain=[("code", "=", "account.payment.order.seq")],
    )
