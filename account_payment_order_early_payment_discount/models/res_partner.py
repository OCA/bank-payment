# Copyright 2026 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    preferred_supplier = fields.Boolean(
        help="Preferred for payment: its bills are paid on their early "
        "payment date, never on their credit term. Confirming a payment "
        "order pulls in the bills whose early payment falls on the day the "
        "order pays, and they stay in the order.",
    )
