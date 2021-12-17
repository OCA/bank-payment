# Copyright 2014-2016 Akretion - Alexis de Lattre
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_mode_id = fields.Many2one(
        'account.payment.mode', string='Payment Mode',
        domain=[('payment_type', '=', 'inbound')])

    def _get_payment_mode_vals(self, vals):
        if self.payment_mode_id:
            vals['payment_mode_id'] = self.payment_mode_id.id
            if self.payment_mode_id.bank_account_link == 'fixed':
                vals['partner_bank_id'] =\
                    self.payment_mode_id.fixed_journal_id.bank_account_id.id
        return vals

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super().onchange_partner_id()
        if self.partner_id:
            self.payment_mode_id = self.partner_id.customer_payment_mode_id
        else:
            self.payment_mode_id = False
        return res

    @api.multi
    def _prepare_invoice(self):
        """Copy bank partner from sale order to invoice"""
        vals = super()._prepare_invoice()
        return self._get_payment_mode_vals(vals)
