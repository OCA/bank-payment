# Copyright 2016 Akretion - Alexis de Lattre
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        """Copy payment mode from sale order to invoice"""
        inv = super()._create_invoice(order, so_line, amount)
        vals = order._get_payment_mode_vals({})
        if vals:
            inv.write(vals)
        return inv
