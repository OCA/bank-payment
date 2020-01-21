# Copyright 2016 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    initiating_party_issuer = fields.Char(
        related="company_id.initiating_party_issuer", readonly=False
    )
    initiating_party_identifier = fields.Char(
        related="company_id.initiating_party_identifier", readonly=False
    )
    initiating_party_scheme = fields.Char(
        related="company_id.initiating_party_scheme", readonly=False
    )
    group_pain_multiple_identifier = fields.Boolean(
        string="Multiple identifiers",
        implied_group="account_banking_pain_base." "group_pain_multiple_identifier",
        help="Enable this option if your country requires several SEPA/PAIN "
        "identifiers like in Spain.",
    )
