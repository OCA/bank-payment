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

from openerp.osv import orm, fields


class sale_order(orm.Model):
    _inherit = "sale.order"

    _columns = {
        'payment_mode_id': fields.many2one(
            'payment.mode', 'Payment Mode'),
    }

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        res = super(sale_order, self).onchange_partner_id(
            cr, uid, ids, part, context=context)
        if part:
            partner = self.pool['res.partner'].browse(
                cr, uid, part, context=context)
            res['value']['payment_mode_id'] = \
                partner.customer_payment_mode.id or False
        else:
            res['value']['payment_mode_id'] = False
        return res

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        """Copy bank partner from sale order to invoice"""
        invoice_vals = super(sale_order, self)._prepare_invoice(
            cr, uid, order, lines, context=context)
        invoice_vals.update({
            'payment_mode_id': order.payment_mode_id.id or False,
            'partner_bank_id': order.payment_mode_id and
            order.payment_mode_id.bank_id.id or False,
        })
        return invoice_vals
