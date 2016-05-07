# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        """Copy mandate from sale order to invoice"""
        inv = super(SaleAdvancePaymentInv, self)._create_invoice(
            order, so_line, amount)
        if order.mandate_id:
            inv.mandate_id = order.mandate_id.id
        return inv
