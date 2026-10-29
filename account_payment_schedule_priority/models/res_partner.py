# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

from .account_move_line import PAYMENT_PRIORITIES


class ResPartner(models.Model):
    _inherit = "res.partner"

    payment_priority = fields.Selection(
        selection=PAYMENT_PRIORITIES,
        default="3",
        help="Priority of the bills of this partner in the payment schedule. When "
        "cash is short, the lowest priorities are paid later; critical ones are "
        "never moved.",
    )
