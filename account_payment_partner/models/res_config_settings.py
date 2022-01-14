# Copyright 2022 - CampToCamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    force_blank_partner_bank_id = fields.Boolean(
        related="company_id.force_blank_partner_bank_id",
        readonly=False,
    )
