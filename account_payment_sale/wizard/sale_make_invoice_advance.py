# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        """Copy payment mode from sale order to invoice"""
        inv = super(SaleAdvancePaymentInv, self)._create_invoice(
            order, so_line, amount)
        vals = {}
        if order.payment_mode_id:
            vals['payment_mode_id'] = order.payment_mode_id.id
            if order.payment_mode_id.bank_account_link == 'fixed':
                vals['partner_bank_id'] =\
                    order.payment_mode_id.fixed_journal_id.bank_account_id.id
        if vals:
            inv.write(vals)
        return inv
