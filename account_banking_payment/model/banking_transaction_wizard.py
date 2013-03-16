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


class banking_transaction_wizard(orm.TransientModel):
    _inherit = 'banking.transaction.wizard'
    _columns = {
        'payment_line_id': fields.related(
            'import_transaction_id', 'payment_line_id', string="Matching payment or storno", 
            type='many2one', relation='payment.line', readonly=True),
        'payment_order_ids': fields.related(
            'import_transaction_id', 'payment_order_ids', string="Matching payment orders", 
            type='many2many', relation='payment.order'),
        'payment_order_id': fields.related(
            'import_transaction_id', 'payment_order_id', string="Payment order to reconcile", 
            type='many2one', relation='payment.order'),
        }
