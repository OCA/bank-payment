##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#              (C) 2011 - 2013 Therp BV (<http://therp.nl>).
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp.tools.translate import _


class clieop_export(orm.Model):
    '''ClieOp3 Export'''
    _name = 'banking.export.clieop'
    _description = __doc__
    _rec_name = 'identification'

    _columns = {
        'payment_order_ids': fields.many2many(
            'payment.order',
            'account_payment_order_clieop_rel',
            'banking_export_clieop_id', 'account_order_id',
            'Payment Orders',
            readonly=True),
        'testcode':
            fields.selection([('T', _('Yes')), ('P', _('No'))],
                             'Test Run', readonly=True),
        'daynumber':
            fields.integer('ClieOp Transaction nr of the Day', readonly=True),
        'duplicates':
            fields.integer('Number of Duplicates', readonly=True),
        'prefered_date':
            fields.date('Prefered Processing Date', readonly=True),
        'no_transactions':
            fields.integer('Number of Transactions', readonly=True),
        'check_no_accounts':
            fields.char('Check Number Accounts', size=5, readonly=True),
        'total_amount':
            fields.float('Total Amount', readonly=True),
        'identification':
            fields.char('Identification', size=6, readonly=True, select=True),
        'filetype':
            fields.selection(
                [
                    ('CREDBET', 'Payment Batch'),
                    ('SALARIS', 'Salary Payment Batch'),
                    ('INCASSO', 'Direct Debit Batch'),
                ],
                'File Type', size=7, readonly=True, select=True),
        'date_generated':
            fields.date('Generation Date', readonly=True, select=True),
        'file':
            fields.binary('ClieOp File', readonly=True,),
        'filename': fields.char(
            'File Name', size=32,
        ),
        'state':
            fields.selection([
                ('draft', 'Draft'),
                ('sent', 'Sent'),
                ('done', 'Reconciled'),
            ], 'State', readonly=True),
    }

    def get_daynr(self, cr, uid, context=None):
        '''
        Return highest day number
        '''
        last = 1
        last_ids = self.search(cr, uid, [
            ('date_generated', '=', fields.date.context_today(
                self, cr, uid, context)),
        ], context=context)
        if last_ids:
            last = 1 + max([x['daynumber'] for x in self.read(
                cr, uid, last_ids, ['daynumber'], context=context)]
            )
        return last

    _defaults = {
        'date_generated': fields.date.context_today,
        'duplicates': 1,
        'state': 'draft',
        'daynumber': get_daynr,
    }
