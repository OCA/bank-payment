# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account Payment Partner module for OpenERP
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


class res_partner(orm.Model):
    _inherit = 'res.partner'

    _columns = {
        'supplier_payment_mode': fields.property(
            'payment.mode', type='many2one', relation='payment.mode',
            string='Supplier Payment Mode', view_load=True,
            help="Select the default payment mode for this supplier."),
        'customer_payment_mode': fields.property(
            'payment.mode', type='many2one', relation='payment.mode',
            string='Customer Payment Mode', view_load=True,
            help="Select the default payment mode for this customer."),
    }

    def _commercial_fields(self, cr, uid, context=None):
        res = super(res_partner, self)._commercial_fields(
            cr, uid, context=context)
        res += ['supplier_payment_mode', 'customer_payment_mode']
        return res
