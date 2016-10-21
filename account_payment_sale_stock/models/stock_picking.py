# -*- coding: utf-8 -*-
##############################################################################
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
        inv_type = self.env.context.get('inv_type', 'out_invoice')
        if picking and picking.sale_id and inv_type == 'out_invoice':
            sale_order = picking.sale_id
            if sale_order.payment_mode_id:
                vals['partner_bank_id'] = sale_order.payment_mode_id.bank_id.id
                vals['payment_mode_id'] = sale_order.payment_mode_id.id
        return super(StockPicking, self)._create_invoice_from_picking(
            picking, vals)
