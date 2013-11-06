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

from openerp.osv import orm, fields
from openerp.addons.decimal_precision import decimal_precision as dp
from unidecode import unidecode


class banking_export_sepa(orm.Model):
    '''SEPA export'''
    _name = 'banking.export.sepa'
    _description = __doc__
    _rec_name = 'filename'

    def _generate_filename(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for sepa_file in self.browse(cr, uid, ids, context=context):
            ref = sepa_file.payment_order_ids[0].reference
            if ref:
                label = unidecode(ref.replace('/', '-'))
            else:
                label = 'error'
            res[sepa_file.id] = 'sct_%s.xml' % label
        return res

    _columns = {
        'payment_order_ids': fields.many2many(
            'payment.order',
            'account_payment_order_sepa_rel',
            'banking_export_sepa_id', 'account_order_id',
            'Payment Orders',
            readonly=True),
        'prefered_exec_date': fields.date(
            'Prefered Execution Date', readonly=True),
        'nb_transactions': fields.integer(
            'Number of Transactions', readonly=True),
        'total_amount': fields.float('Total Amount',
            digits_compute=dp.get_precision('Account'), readonly=True),
        'batch_booking': fields.boolean(
            'Batch Booking', readonly=True,
            help="If true, the bank statement will display only one debit line for all the wire transfers of the SEPA XML file ; if false, the bank statement will display one debit line per wire transfer of the SEPA XML file."),
        'charge_bearer': fields.selection([
            ('SHAR', 'Shared'),
            ('CRED', 'Borne by Creditor'),
            ('DEBT', 'Borne by Debtor'),
            ('SLEV', 'Following Service Level'),
            ], 'Charge Bearer', readonly=True,
            help='Shared : transaction charges on the sender side are to be borne by the debtor, transaction charges on the receiver side are to be borne by the creditor (most transfers use this). Borne by creditor : all transaction charges are to be borne by the creditor. Borne by debtor : all transaction charges are to be borne by the debtor. Following service level : transaction charges are to be applied following the rules agreed in the service level and/or scheme.'),
        'create_date': fields.datetime('Generation Date', readonly=True),
        'file': fields.binary('SEPA XML File', readonly=True),
        'filename': fields.function(
            _generate_filename, type='char', size=256, string='Filename',
            readonly=True),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('sent', 'Sent'),
            ('done', 'Reconciled'),
            ], 'State', readonly=True),
    }

    _defaults = {
        'state': 'draft',
    }
