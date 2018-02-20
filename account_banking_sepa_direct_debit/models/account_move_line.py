# -*- coding: utf-8 -*-
# © 2018 Comunitea Servicios Tescnológicos S.L. - Omar Castiñeira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    mandate_scheme = fields.Selection([
        ('CORE', 'Basic (CORE)'),
        ('B2B', 'Enterprise (B2B)')],
        string='Mandate Scheme', related="mandate_id.scheme", readonly=True)
