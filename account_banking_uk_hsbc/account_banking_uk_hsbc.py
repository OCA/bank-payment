##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#    Copyright (C) 2011 credativ Ltd (<http://www.credativ.co.uk>).
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
from datetime import date
from tools.translate import _

class hsbc_export(osv.osv):
    '''HSBC Export'''
    _name = 'banking.export.hsbc'
    _description = __doc__
    _rec_name = 'execution_date'

    _columns = {
        'payment_order_ids': fields.many2many(
            'payment.order',
            'account_payment_order_hsbc_rel',
            'banking_export_hsbc_id', 'account_order_id',
            'Payment Orders',
            readonly=True),
        'identification':
            fields.char('Identification', size=15, readonly=True, select=True),
        'execution_date':
            fields.date('Execution Date',readonly=True),
        'no_transactions':
            fields.integer('Number of Transactions', readonly=True),
        'total_amount':
            fields.float('Total Amount', readonly=True),
        'date_generated':
            fields.datetime('Generation Date', readonly=True, select=True),
        'file':
            fields.binary('HSBC File', readonly=True),
        'state':
            fields.selection([
                ('draft', 'Draft'),
                ('sent', 'Sent'),
                ('done', 'Reconciled'),
            ], 'State', readonly=True),
    }

    _defaults = {
        'date_generated': lambda *a: date.today().strftime('%Y-%m-%d'),
        'state': lambda *a: 'draft',
    }
hsbc_export()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
