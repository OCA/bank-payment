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

from openerp.osv import orm, fields


class purchase_order(orm.Model):
    _inherit = "purchase.order"

    _columns = {
        'supplier_partner_bank_id': fields.many2one(
            'res.partner.bank', 'Supplier Bank Account',
            help="Select the bank account of your supplier on which "
            "your company should send the payment. This field is copied "
            "from the partner and will be copied to the supplier invoice."),
        'payment_mode_id': fields.many2one(
            'payment.mode', 'Payment Mode'),
    }

    def _get_default_supplier_partner_bank(
            self, cr, uid, partner, context=None):
        '''This function is designed to be inherited'''
        if partner.bank_ids:
            return partner.bank_ids[0].id
        else:
            return False

    def onchange_partner_id(self, cr, uid, ids, partner_id):
        res = super(purchase_order, self).onchange_partner_id(
            cr, uid, ids, partner_id)
        if partner_id:
            partner = self.pool['res.partner'].browse(
                cr, uid, partner_id)
            res['value'].update({
                'supplier_partner_bank_id':
                self._get_default_supplier_partner_bank(
                    cr, uid, partner),
                'payment_mode_id':
                partner.supplier_payment_mode.id or False,
            })
        else:
            res['value'].update({
                'supplier_partner_bank_id': False,
                'payment_mode_id': False,
            })
        return res

    def action_invoice_create(self, cr, uid, ids, context=None):
        """Copy bank partner + payment type from PO to invoice"""
        # as of OpenERP 7.0, there is no _prepare function for
        # the invoice (the _prepare function only exists for invoice lines)
        res = super(purchase_order, self).action_invoice_create(
            cr, uid, ids, context=context)
        for order in self.browse(cr, uid, ids, context=context):
            for invoice in order.invoice_ids:
                if invoice.state == 'draft':
                    invoice.write(
                        {
                            'partner_bank_id':
                            order.supplier_partner_bank_id.id or False,
                            'payment_mode_id':
                            order.payment_mode_id.id or False,
                        },
                        context=context)
        return res
