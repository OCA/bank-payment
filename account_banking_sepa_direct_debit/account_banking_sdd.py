##############################################################################
#
#    SEPA Direct Debit module for OpenERP
#    Copyright (C) 2013 Akretion (http://www.akretion.com)
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
from openerp.tools.translate import _
from openerp.addons.decimal_precision import decimal_precision as dp
from unidecode import unidecode
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

NUMBER_OF_UNUSED_MONTHS_BEFORE_EXPIRY = 36

logger = logging.getLogger(__name__)


class banking_export_sdd(orm.Model):
    '''SEPA Direct Debit export'''
    _name = 'banking.export.sdd'
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
            res[sepa_file.id] = 'sdd_%s.xml' % label
        return res

    _columns = {
        'payment_order_ids': fields.many2many(
            'payment.order',
            'account_payment_order_sdd_rel',
            'banking_export_sepa_id', 'account_order_id',
            'Payment Orders',
            readonly=True),
        'requested_collec_date': fields.date(
            'Requested Collection Date', readonly=True),
        'nb_transactions': fields.integer(
            'Number of Transactions', readonly=True),
        'total_amount': fields.float(
            'Total Amount', digits_compute=dp.get_precision('Account'),
            readonly=True),
        'batch_booking': fields.boolean(
            'Batch Booking', readonly=True,
            help="If true, the bank statement will display only one credit line for all the direct debits of the SEPA XML file ; if false, the bank statement will display one credit line per direct debit of the SEPA XML file."),
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
            _generate_filename, type='char', size=256,
            string='Filename', readonly=True, store=True),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('sent', 'Sent'),
            ('done', 'Reconciled'),
            ], 'State', readonly=True),
    }

    _defaults = {
        'state': 'draft',
    }


class sdd_mandate(orm.Model):
    '''SEPA Direct Debit Mandate'''
    _name = 'sdd.mandate'
    _description = __doc__
    _rec_name = 'unique_mandate_reference'
    _inherit = ['mail.thread']
    _order = 'signature_date desc'
    _track = {
        'state': {
            'account_banking_sepa_direct_debit.mandate_valid':
                lambda self, cr, uid, obj, ctx=None: obj['state'] == 'valid',
            'account_banking_sepa_direct_debit.mandate_expired':
                lambda self, cr, uid, obj, ctx=None: obj['state'] == 'expired',
            }
        }

    _columns = {
        'partner_bank_id': fields.many2one('res.partner.bank', 'Bank Account'),
        'partner_id': fields.related(
            'partner_bank_id', 'partner_id', type='many2one',
            relation='res.partner', string='Partner', readonly=True),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'unique_mandate_reference': fields.char(
            'Unique Mandate Reference', size=35, readonly=True),
        'type': fields.selection([
            ('recurrent', 'Recurrent'),
            ('oneoff', 'One-Off'),
            ], 'Type of Mandate', required=True),
        'signature_date': fields.date('Date of Signature of the Mandate'),
        'scan': fields.binary('Scan of the mandate'),
        'last_debit_date': fields.date(
            'Date of the Last Debit',
            help="For recurrent mandates, this field is used to know if the SDD will be of type 'First' or 'Recurring'. For one-off mandates, this field is used to know if the SDD has already been used or not."),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('valid', 'Valid'),
            ('expired', 'Expired'),
            # Do we have to handle cancellation of mandate by customer ?
            ], 'Mandate Status',
            help="For a recurrent mandate, this field indicate if the mandate is still valid or if it has expired (a recurrent mandate expires if it's not used during 36 months). For a one-off mandate, it expires after its first use."),
        'payment_line_ids': fields.one2many(
            'payment.line', 'sdd_mandate_id', "Related Payment Lines"),
        }

    _defaults = {
        'company_id': lambda self, cr, uid, context:
            self.pool['res.company'].\
            _company_default_get(cr, uid, 'sdd.mandate', context=context),
        'unique_mandate_reference': lambda self, cr, uid, ctx:
            self.pool['ir.sequence'].get(cr, uid, 'sdd.mandate.reference'),
        'state': 'draft',
    }

    _sql_constraints = [(
        'mandate_ref_company_uniq',
        'unique(unique_mandate_reference, company_id)',
        'A Mandate with the same reference already exists for this company !'
        )]

    def _check_sdd_mandate(self, cr, uid, ids, context=None):
        for mandate in self.read(cr, uid, ids, [
                'last_debit_date', 'signature_date',
                'unique_mandate_reference', 'state', 'partner_bank_id'
                ], context=context):
            if (mandate['signature_date'] and
                    mandate['signature_date'] >
                    datetime.today().strftime('%Y-%m-%d')):
                raise orm.except_orm(
                    _('Error:'),
                    _("The date of signature of mandate '%s' is in the future!")
                    % mandate['unique_mandate_reference'])
            if mandate['state'] == 'valid' and not mandate['signature_date']:
                raise orm.except_orm(
                    _('Error:'),
                    _("Cannot validate the mandate '%s' without a date of signature.")
                    % mandate['unique_mandate_reference'])
            if mandate['state'] == 'valid' and not mandate['partner_bank_id']:
                raise orm.except_orm(
                    _('Error:'),
                    _("Cannot validate the mandate '%s' because it is not linked to a bank account.")
                    % mandate['unique_mandate_reference'])

            if (mandate['signature_date'] and mandate['last_debit_date'] and
                    mandate['signature_date'] > mandate['last_debit_date']):
                raise orm.except_orm(
                    _('Error:'),
                    _("The mandate '%s' can't have a date of last debit before the date of signature.")
                    % mandate['unique_mandate_reference'])
        return True

    _constraints = [
        (_check_sdd_mandate, "Error msg in raise",
            ['last_debit_date', 'signature_date', 'state', 'partner_bank_id']),
    ]

    def validate(self, cr, uid, ids, context=None):
        to_validate_ids = []
        for mandate in self.browse(cr, uid, ids, context=context):
            assert mandate.state == 'draft', 'Mandate should be in draft state'
            to_validate_ids.append(mandate.id)
        self.write(
            cr, uid, to_validate_ids, {'state': 'valid'}, context=context)
        return True

    def _sdd_mandate_set_state_to_expired(self, cr, uid, context=None):
        logger.info('Searching for SDD Mandates that must be set to Expired')
        expire_limit_date = datetime.today() + \
            relativedelta(months=-NUMBER_OF_UNUSED_MONTHS_BEFORE_EXPIRY)
        expire_limit_date_str = expire_limit_date.strftime('%Y-%m-%d')
        expired_mandate_ids = self.search(cr, uid, [
            '|',
            ('last_debit_date', '=', False),
            ('last_debit_date', '<=', expire_limit_date_str),
            ('state', '=', 'valid'),
            ('signature_date', '<=', expire_limit_date_str),
            ], context=context)
        if expired_mandate_ids:
            self.write(
                cr, uid, expired_mandate_ids, {'state': 'expired'},
                context=context)
            logger.info(
                'The following SDD Mandate IDs has been set to expired: %s'
                % expired_mandate_ids)
        else:
            logger.info('0 SDD Mandates must be set to Expired')
        return True


class res_partner_bank(orm.Model):
    _inherit = 'res.partner.bank'

    _columns = {
        'sdd_mandate_ids': fields.one2many(
            'sdd.mandate', 'partner_bank_id', 'SEPA Direct Debit Mandates'),
        }


class payment_line(orm.Model):
    _inherit = 'payment.line'

    _columns = {
        'sdd_mandate_id': fields.many2one(
            'sdd.mandate', 'SEPA Direct Debit Mandate'),
        }

    def create(self, cr, uid, vals, context=None):
        '''Take the first valid mandate of the bank account by default'''
        if context is None:
            context = {}
        if not vals:
            vals = {}
        partner_bank_id = vals.get('bank_id')
        if (context.get('default_payment_order_type') == 'debit'
                and partner_bank_id
                and 'sdd_mandate_id' not in vals):
            mandate_ids = self.pool['sdd.mandate'].search(cr, uid, [
                ('partner_bank_id', '=', partner_bank_id),
                ('state', '=', 'valid'),
                ], context=context)
            if mandate_ids:
                vals['sdd_mandate_id'] = mandate_ids[0]
        return super(payment_line, self).create(cr, uid, vals, context=context)
