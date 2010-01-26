##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
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

class payment_order(osv.osv):
    '''
    Attach export_clieop wizard to payment order and allow traceability
    '''
    _inherit = 'payment.order'
    def get_wizard(self, type):
        if type in ['CLIEOPPAY', 'CLIEOPINC', 'CLIEOPSAL']:
            return self._module, 'wizard_account_banking_export_clieop'
        return super(payment_order, self).get_wizard(type)
payment_order()

class clieop_export(osv.osv):
    '''ClieOp3 Export'''
    _name = 'banking.export.clieop'
    _description = __doc__

    _columns = {
        'payment_order_ids':
            fields.text('Payment Orders'),
        'testcode':
            fields.selection([('T', _('Yes')), ('P', _('No'))],
                             'Test Run', readonly=True),
        'daynumber':
            fields.integer('ClieOp Transaction nr of the Day', readonly=True),
        'duplicates':
            fields.integer('Number of Duplicates', readonly=True),
        'prefered_date':
            fields.date('Prefered Processing Date',readonly=True),
        'no_transactions':
            fields.integer('Number of Transactions', readonly=True),
        'check_no_accounts':
            fields.char('Check Number Accounts', size=5, readonly=True),
        'total_amount':
            fields.float('Total Amount', readonly=True),
        'identification':
            fields.char('Identification', size=6, readonly=True, select=True),
        'filetype':
            fields.selection([
                ('CREDBET', 'Payment Batch'),
                ('SALARIS', 'Salary Payment Batch'),
                ('INCASSO', 'Direct Debit Batch'),
                ], 'File Type', size=7, readonly=True, select=True),
        'date_generated':
            fields.datetime('Generation Date', readonly=True, select=True),
        'file':
            fields.binary('ClieOp File', readonly=True),
        'state':
            fields.selection([
                ('draft', 'Draft'),
                ('sent', 'Sent'),
                ('done', 'Reconciled'),
            ], 'State', readonly=True),
    }
    def _get_daynr(self, cursor, uid, ids, context):
        '''
        Return highest day number
        '''
        last = cursor.execute('SELECT max(daynumber) '
                              'FROM banking_export_clieop '
                              'WHERE date_generated = "%s"' % 
                              date.today().strftime('%Y-%m-%d')
                             ).fetchone()
        if last:
            return int(last) +1
        return 1

    _defaults = {
        'date_generated': lambda *a: date.today().strftime('%Y-%m-%d'),
        'duplicates': lambda *a: 1,
        'state': lambda *a: 'draft',
        'daynumber': _get_daynr,
    }
clieop_export()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
