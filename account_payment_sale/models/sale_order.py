# -*- coding: utf-8 -*-
# © 2014-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_mode_id = fields.Many2one(
        'account.payment.mode', string='Payment Mode',
        domain=[('payment_type', '=', 'inbound')])

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(SaleOrder, self).onchange_partner_id()
        if self.partner_id:
            self.payment_mode_id = self.partner_id.customer_payment_mode_id
        else:
            self.payment_mode_id = False
        return res

    @api.multi
    def _prepare_invoice(self):
        """Copy bank partner from sale order to invoice"""
        vals = super(SaleOrder, self)._prepare_invoice()
        if self.payment_mode_id:
            vals['payment_mode_id'] = self.payment_mode_id.id
            if self.payment_mode_id.bank_account_link == 'fixed':
                vals['partner_bank_id'] =\
                    self.payment_mode_id.fixed_journal_id.bank_account_id.id
        return vals
