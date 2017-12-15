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
        if picking and picking.sale_id:
            sale_order = picking.sale_id
            if sale_order.payment_mode_id:
                vals['partner_bank_id'] = sale_order.payment_mode_id.bank_id.id
                vals['payment_mode_id'] = sale_order.payment_mode_id.id
            #a second chance to get the payment mode if not found at sale_order
            if 'payment_mode_id' not in vals or not vals['payment_mode_id']:
                #partner to invoice is not always the same partner of
                #the picking, so we get the partner from vals
                partner = self.env['res.partner'].browse(vals['partner_id'])
                #and then we get the payment mode from partner
                vals['payment_mode_id'] = partner.customer_payment_mode.id
                if partner.customer_payment_mode.bank_id:
                    vals['partner_bank_id'] = \
                        partner.customer_payment_mode.bank_id.id
        return super(StockPicking, self)._create_invoice_from_picking(
            picking, vals)
