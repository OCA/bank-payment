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

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    supplier_partner_bank_id = fields.Many2one(
        comodel_name='res.partner.bank', string='Supplier Bank Account',
        domain=[('partner_id', '=', 'partner_id')],
        help="Select the bank account of your supplier on which your company "
             "should send the payment. This field is copied from the partner "
             "and will be copied to the supplier invoice.")
    payment_mode_id = fields.Many2one(
        comodel_name='account.payment.mode', string='Payment Mode',
        domain=[('purchase_ok', '=', False)],
        help="Select the default payment mode for this purchase order.")

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        self.payment_mode_id = None
        self.supplier_partner_bank_id = None
        res = super(PurchaseOrder, self).onchange_partner_id()
        if self.partner_id.supplier_payment_mode_id \
                and self.partner_id.supplier_payment_mode_id.purchase_ok:
            self.payment_mode_id = \
                self.partner_id.supplier_payment_mode_id or False
        self.supplier_partner_bank_id = \
            self.partner_id.bank_ids and \
            self.partner_id.bank_ids[0].id or False
        return res

    @api.model
    def _get_default_supplier_partner_payment_mode(self, partner):
        """This function is designed to be inherited"""
        return partner.bank_ids and partner.bank_ids[0].id or False

    @api.multi
    def action_view_invoice(self):
        res = super(PurchaseOrder, self).action_view_invoice()
        res['context']['default_partner_bank_id'] = self.onchange_partner_id()
        return res
