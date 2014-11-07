# -*- encoding: utf-8 -*-
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

from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    supplier_partner_bank_id = fields.Many2one(
        'res.partner.bank', string='Supplier Bank Account',
        domain="[('partner_id', '=', partner_id)]",
        help="Select the bank account of your supplier on which your company "
             "should send the payment. This field is copied from the partner "
             "and will be copied to the supplier invoice.")
    payment_mode_id = fields.Many2one(
        'payment.mode', string='Payment Mode',
        domain="[('purchase_ok', '=', True)]")

    @api.model
    def _get_default_supplier_partner_bank(self, partner):
        """This function is designed to be inherited"""
        return partner.bank_ids and partner.bank_ids[0].id or False

    @api.multi
    def onchange_partner_id(self, partner_id):
        res = super(PurchaseOrder, self).onchange_partner_id(partner_id)
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            res['value']['supplier_partner_bank_id'] = \
                self._get_default_supplier_partner_bank(partner)
            res['value']['payment_mode_id'] = partner.supplier_payment_mode.id
        else:
            res['value']['supplier_partner_bank_id'] = False
            res['value']['payment_mode_id'] = False
        return res

    @api.model
    def _prepare_invoice(self, order, line_ids):
        res = super(PurchaseOrder, self)._prepare_invoice(order, line_ids)
        if order:
            res['partner_bank_id'] = order.supplier_partner_bank_id.id
            res['payment_mode_id'] = order.payment_mode_id.id
        return res
