# -*- encoding: utf-8 -*-
##############################################################################
#
#    French Letter of Change module for Odoo
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
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
from openerp.addons.decimal_precision import decimal_precision as dp
from unidecode import unidecode


class banking_export_lcr(orm.Model):
    '''French LCR'''
    _name = 'banking.export.lcr'
    _description = __doc__
    _rec_name = 'filename'

    def _generate_filename(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for lcr_file in self.browse(cr, uid, ids, context=context):
            ref = lcr_file.payment_order_ids[0].reference
            if ref:
                label = unidecode(ref.replace('/', '-'))
            else:
                label = 'error'
            res[lcr_file.id] = 'lcr_%s.txt' % label
        return res

    _columns = {
        'payment_order_ids': fields.many2many(
            'payment.order',
            'account_payment_order_lcr_rel',
            'banking_export_lcr_id', 'payment_order_id',
            'Payment Orders',
            readonly=True),
        'nb_transactions': fields.integer(
            'Number of Transactions', readonly=True),
        'total_amount': fields.float(
            'Total Amount', digits_compute=dp.get_precision('Account'),
            readonly=True),
        'create_date': fields.datetime('Generation Date', readonly=True),
        'file': fields.binary('CFONB File', readonly=True),
        'filename': fields.function(
            _generate_filename, type='char', size=256,
            string='Filename', readonly=True, store=True),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('sent', 'Sent'),
            ], 'State', readonly=True),
    }

    _defaults = {
        'state': 'draft',
    }
