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

from openerp.osv import orm


class stock_picking(orm.Model):
    _inherit = "stock.picking"

    def _prepare_invoice(
            self, cr, uid, picking, partner, inv_type, journal_id,
            context=None):
        """Copy bank partner and payment type from PO to invoice"""
        invoice_vals = super(stock_picking, self)._prepare_invoice(
            cr, uid, picking, partner, inv_type, journal_id, context=context)
        if picking.purchase_id:
            invoice_vals.update({
                'partner_bank_id':
                picking.purchase_id.supplier_partner_bank.id or False,
                'payment_mode_type':
                picking.purchase_id.payment_mode_type.id or False,
                })
        return invoice_vals
