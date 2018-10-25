# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    sepa_creditor_identifier = fields.Char(
        related='company_id.sepa_creditor_identifier')

    sepa_payment_order_schema = fields.Selection(
        related='company_id.sepa_payment_order_schema'
    )
