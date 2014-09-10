# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account Payment Sale module for OpenERP
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

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_mode_id = fields.Many2one(
        'payment.mode', string='Payment Mode',
        domain="[('sale_ok', '=', True)]")

    @api.multi
    def onchange_partner_id(self, partner_id):
        res = super(SaleOrder, self).onchange_partner_id(partner_id)
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            res['value']['payment_mode_id'] = partner.customer_payment_mode.id
        else:
            res['value']['payment_mode_id'] = False
        return res

    @api.model
    def _prepare_invoice(self, order, lines):
        """Copy bank partner from sale order to invoice"""
        vals = super(SaleOrder, self)._prepare_invoice(order, lines)
        if order.payment_mode_id:
            vals['payment_mode_id'] = order.payment_mode_id.id
            vals['partner_bank_id'] = order.payment_mode_id.bank_id.id
        return vals
