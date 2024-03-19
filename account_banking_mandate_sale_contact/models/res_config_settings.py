# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_default_mandate_contact = fields.Selection(
        string="Default Sale Mandate Contact",
        related="company_id.sale_default_mandate_contact",
        readonly=False,
    )
