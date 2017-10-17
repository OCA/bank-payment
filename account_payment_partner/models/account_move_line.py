# -*- coding: utf-8 -*-
# © 2016 Akretion (https://www.akretion.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    payment_mode_id = fields.Many2one(
        'account.payment.mode',
        string='Payment Mode',
        domain="[('company_id', '=', company_id)]",
        ondelete='restrict'
    )
