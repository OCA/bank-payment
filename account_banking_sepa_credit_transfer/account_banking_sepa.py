##############################################################################
#
#    SEPA Credit Transfer module for OpenERP
#    Copyright (C) 2010-2013 Akretion (http://www.akretion.com)
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

from osv import osv, fields
import time
from tools.translate import _
import decimal_precision as dp


class banking_export_sepa(osv.osv):
    '''SEPA export'''
    _name = 'banking.export.sepa'
    _description = __doc__
    _rec_name = 'msg_identification'

    def _generate_filename(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for sepa_file in self.browse(cr, uid, ids, context=context):
            res[sepa_file.id] = 'sepa_' + (sepa_file.msg_identification or '') + '.xml'
        return res

    _columns = {
        'payment_order_ids': fields.many2many(
            'payment.order',
            'account_payment_order_sepa_rel',
            'banking_export_sepa_id', 'account_order_id',
            'Payment orders',
            readonly=True),
        'prefered_exec_date': fields.date('Prefered execution date', readonly=True),
        'nb_transactions': fields.integer('Number of transactions', readonly=True),
        'total_amount': fields.float('Total amount',
            digits_compute=dp.get_precision('Account'), readonly=True),
        'msg_identification': fields.char('Message identification', size=35,
            readonly=True),
        'batch_booking': fields.boolean('Batch booking', readonly=True,
            help="If true, the bank statement will display only one debit line for all the wire transfers of the SEPA XML file ; if false, the bank statement will display one debit line per wire transfer of the SEPA XML file."),
        'charge_bearer': fields.selection([
            ('SHAR', 'Shared'),
            ('CRED', 'Borne by creditor'),
            ('DEBT', 'Borne by debtor'),
            ('SLEV', 'Following service level'),
            ], 'Charge bearer', readonly=True,
            help='Shared : transaction charges on the sender side are to be borne by the debtor, transaction charges on the receiver side are to be borne by the creditor (most transfers use this). Borne by creditor : all transaction charges are to be borne by the creditor. Borne by debtor : all transaction charges are to be borne by the debtor. Following service level : transaction charges are to be applied following the rules agreed in the service level and/or scheme.'),
        'generation_date': fields.datetime('Generation date',
            readonly=True),
        'file': fields.binary('SEPA XML file', readonly=True),
        'filename': fields.function(_generate_filename, type='char', size=256,
            method=True, string='Filename', readonly=True),
        'state': fields.selection([
                ('draft', 'Draft'),
                ('sent', 'Sent'),
                ('done', 'Reconciled'),
            ], 'State', readonly=True),
    }

    _defaults = {
        'generation_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'state': 'draft',
    }

banking_export_sepa()

