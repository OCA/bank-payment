# Copyright 2016 Akretion - Alexis de Lattre
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sepa_creditor_identifier = fields.Char(
        related="company_id.sepa_creditor_identifier", readonly=False
    )
