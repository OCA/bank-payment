# Copyright 2016-2022 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_invoice_values(self, order, name, amount, so_line):
        """Copy mandate from sale order to invoice"""
        vals = super()._prepare_invoice_values(order, name, amount, so_line)
        if order.mandate_id:
            vals["mandate_id"] = order.mandate_id.id
        return vals
