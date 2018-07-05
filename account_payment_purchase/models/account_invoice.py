# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        if self.env.context.get('default_purchase_id', False):
            self.payment_mode_id = self.env['purchase.order'].search(
                [('id', '=', self.env.context.get('default_purchase_id'))]
            ).payment_mode_id.id
        if self.env.context.get('default_partner_bank_id', False):
            self.partner_bank_id = self.env['purchase.order'].search(
                [('id', '=', self.env.context.get('default_purchase_id'))]
            ).supplier_partner_bank_id.id
        return res
