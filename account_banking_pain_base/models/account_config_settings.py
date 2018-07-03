# -*- coding: utf-8 -*-
# Copyright 2016 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    initiating_party_issuer = fields.Char(
        related='company_id.initiating_party_issuer')
    initiating_party_identifier = fields.Char(
        related='company_id.initiating_party_identifier')
    initiating_party_scheme = fields.Char(
        related='company_id.initiating_party_scheme')
    group_pain_multiple_identifier = fields.Boolean(
        string='Multiple identifiers',
        implied_group='account_banking_pain_base.'
                      'group_pain_multiple_identifier',
        help="Enable this option if your country requires several SEPA/PAIN "
             "identifiers like in Spain.",
    )
