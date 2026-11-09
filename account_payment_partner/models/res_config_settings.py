# Copyright 2026 Engenere - Felipe Motter Pereira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    keep_partner_bank_without_payment_mode = fields.Boolean(
        related="company_id.keep_partner_bank_without_payment_mode",
        readonly=False,
    )
