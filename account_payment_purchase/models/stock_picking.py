# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Payment Purchase module for OpenERP
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _create_invoice_from_picking(self, picking, vals):
        # This will assure that stock_dropshipping_dual_invoice will work
        inv_type = self.env.context.get('inv_type', 'in_invoice')
        if picking and picking.move_lines and inv_type == 'in_invoice':
            # Get purchase order from first move line
            if picking.move_lines[0].purchase_line_id:
                purchase = picking.move_lines[0].purchase_line_id.order_id
                vals['partner_bank_id'] = purchase.supplier_partner_bank_id.id
                vals['payment_mode_id'] = purchase.payment_mode_id.id
        return super(StockPicking, self)._create_invoice_from_picking(
            picking, vals)
