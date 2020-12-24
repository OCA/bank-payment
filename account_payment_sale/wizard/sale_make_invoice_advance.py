# Copyright 2016-2020 Akretion - Alexis de Lattre
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_invoice_values(self, order, name, amount, so_line):
        """Copy payment mode from sale order to invoice"""
        vals = super()._prepare_invoice_values(order, name, amount, so_line)
        order._get_payment_mode_vals(vals)
        return vals
