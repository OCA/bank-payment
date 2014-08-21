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


class banking_import_line(orm.TransientModel):
    _inherit = 'banking.import.line'
    _columns = {
        'payment_order_id': fields.many2one(
            'payment.order', 'Payment order'),
        'transaction_type': fields.selection([
            # Add payment order related transaction types
            ('invoice', 'Invoice payment'),
            ('payment_order_line', 'Payment from a payment order'),
            ('payment_order', 'Aggregate payment order'),
            ('storno', 'Canceled debit order'),
            ('bank_costs', 'Bank costs'),
            ('unknown', 'Unknown'),
        ], 'Transaction type'),
    }
