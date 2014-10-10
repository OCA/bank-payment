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


class payment_mode_type(orm.Model):
    _name = 'payment.mode.type'
    _description = 'Payment Mode Type'
    _columns = {
        'name': fields.char(
            'Name', size=64, required=True,
            help='Payment Type'
        ),
        'code': fields.char(
            'Code', size=64, required=True,
            help='Specify the Code for Payment Type'
        ),
        'suitable_bank_types': fields.many2many(
            'res.partner.bank.type',
            'bank_type_payment_type_rel',
            'pay_type_id', 'bank_type_id',
            'Suitable bank types', required=True),
        'ir_model_id': fields.many2one(
            'ir.model', 'Payment wizard',
            help=('Select the Payment Wizard for payments of this type. '
                  'Leave empty for manual processing'),
            domain=[('osv_memory', '=', True)],
        ),
        'payment_order_type': fields.selection(
            [('payment', 'Payment'), ('debit', 'Direct debit')],
            'Payment order type', required=True,
        ),
        'active': fields.boolean('Active'),
    }

    _defaults = {
        'payment_order_type': 'payment',
        'active': True,
    }

    def _auto_init(self, cr, context=None):
        r = super(payment_mode_type, self)._auto_init(cr, context=context)
        # migrate xmlid from manual_bank_transfer to avoid dependency on
        # account_banking
        cr.execute("""UPDATE ir_model_data
                      SET module='account_banking_payment_export'
                      WHERE module='account_banking' AND
                            name='manual_bank_tranfer' AND
                            model='payment.mode.type'""")
        return r
