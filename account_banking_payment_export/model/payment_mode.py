# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#              (C) 2011 - 2013 Therp BV (<http://therp.nl>).
#
#    All other contributions are (C) by their respective contributors
#
#    All Rights Reserved
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


class payment_mode(orm.Model):
    ''' Restoring the payment type from version 5,
    used to select the export wizard (if any) '''
    _inherit = "payment.mode"

    def suitable_bank_types(self, cr, uid, payment_mode_id=None, context=None):
        """ Reinstates functional code for suitable bank type filtering.
        Current code in account_payment is disfunctional.
        """
        res = []
        payment_mode = self.browse(
            cr, uid, payment_mode_id, context)
        if (payment_mode and
                payment_mode.type and
                payment_mode.type.suitable_bank_types):
            res = [t.code for t in payment_mode.type.suitable_bank_types]
        return res

    _columns = {
        'type': fields.many2one(
            'payment.mode.type', 'Payment type',
            required=True,
            help='Select the Payment Type for the Payment Mode.'
        ),
        'payment_order_type': fields.related(
            'type', 'payment_order_type', readonly=True, type='selection',
            selection=[('payment', 'Payment'), ('debit', 'Direct debit')],
            string="Payment Order Type"),
        'active': fields.boolean('Active'),
    }

    _defaults = {
        'active': True,
    }
