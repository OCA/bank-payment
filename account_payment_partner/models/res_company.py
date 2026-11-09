# Copyright 2026 Engenere - Felipe Motter Pereira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    keep_partner_bank_without_payment_mode = fields.Boolean(
        string="Keep Bank Account Without Payment Mode",
        default=True,
        help="When enabled, invoices without a payment mode will keep "
        "the bank account auto-selected by Odoo. When disabled, "
        "the bank account will be cleared if no payment mode is set.",
    )
