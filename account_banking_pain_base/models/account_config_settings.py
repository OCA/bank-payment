# -*- coding: utf-8 -*-
# © 2016 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    initiating_party_issuer = fields.Char(
        related='company_id.initiating_party_issuer')
    initiating_party_identifier = fields.Char(
        related='company_id.initiating_party_identifier')
