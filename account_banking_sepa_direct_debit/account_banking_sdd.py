# -*- coding: utf-8 -*-
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
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

try:
    from unidecode import unidecode
except ImportError:
    unidecode = None

NUMBER_OF_UNUSED_MONTHS_BEFORE_EXPIRY = 36

logger = logging.getLogger(__name__)


class banking_export_sdd(orm.Model):
    '''SEPA Direct Debit export'''
    _name = 'banking.export.sdd'
    _description = 'SEPA Direct Debit export'
    _rec_name = 'filename'

    def _generate_filename(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for sepa_file in self.browse(cr, uid, ids, context=context):
            if not sepa_file.payment_order_ids:
                label = 'no payment order'
            else:
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
        'nb_transactions': fields.integer(
            'Number of Transactions', readonly=True),
        'total_amount': fields.float(
            'Total Amount', digits_compute=dp.get_precision('Account'),
            readonly=True),
        'batch_booking': fields.boolean(
            'Batch Booking', readonly=True,
            help="If true, the bank statement will display only one credit "
            "line for all the direct debits of the SEPA file ; if false, "
            "the bank statement will display one credit line per direct "
            "debit of the SEPA file."),
        'charge_bearer': fields.selection([
            ('SLEV', 'Following Service Level'),
            ('SHAR', 'Shared'),
            ('CRED', 'Borne by Creditor'),
            ('DEBT', 'Borne by Debtor'),
        ], 'Charge Bearer', readonly=True,
            help="Following service level : transaction charges are to be "
            "applied following the rules agreed in the service level and/or "
            "scheme (SEPA Core messages must use this). Shared : "
            "transaction charges on the creditor side are to be borne by "
            "the creditor, transaction charges on the debtor side are to be "
            "borne by the debtor. Borne by creditor : all transaction "
            "charges are to be borne by the creditor. Borne by debtor : "
            "all transaction charges are to be borne by the debtor."),
        'create_date': fields.datetime('Generation Date', readonly=True),
        'file': fields.binary('SEPA File', readonly=True),
        'filename': fields.function(
            _generate_filename, type='char', size=256,
            string='Filename', readonly=True, store=True),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('sent', 'Sent'),
        ], 'State', readonly=True),
    }

    _defaults = {
        'state': 'draft',
    }


class sdd_mandate(orm.Model):
    '''SEPA Direct Debit Mandate'''
    _name = 'account.banking.mandate'
    _description = 'SEPA Direct Debit Mandate'
    _inherit = 'account.banking.mandate'
    _track = {
        'recurrent_sequence_type': {
            'account_banking_sepa_direct_debit.recurrent_sequence_type_first':
            lambda self, cr, uid, obj, ctx=None:
            obj['recurrent_sequence_type'] == 'first',
            'account_banking_sepa_direct_debit.'
            'recurrent_sequence_type_recurring':
            lambda self, cr, uid, obj, ctx=None:
            obj['recurrent_sequence_type'] == 'recurring',
            'account_banking_sepa_direct_debit.recurrent_sequence_type_final':
            lambda self, cr, uid, obj, ctx=None:
            obj['recurrent_sequence_type'] == 'final',
        }
    }

    def _get_type(self, cr, uid, context=None):
        return [
            ('recurrent', _('Recurrent')),
            ('oneoff', _('One-Off')),
        ]

    def _get_recurrent_sequence_type(self, cr, uid, context=None):
        return [
            ('first', _('First')),
            ('recurring', _('Recurring')),
            ('final', _('Final')),
        ]

    _columns = {
        'type': fields.selection(
            lambda self, *a, **kw: self._get_type(*a, **kw),
            string='Type of Mandate',
            required=True, track_visibility='always'
        ),
        'recurrent_sequence_type': fields.selection(
            lambda self, *a, **kw: self._get_recurrent_sequence_type(*a, **kw),
            string='Sequence Type for Next Debit',
            track_visibility='onchange',
            help="This field is only used for Recurrent mandates, not for "
            "One-Off mandates."
        ),
        'sepa_migrated': fields.boolean(
            'Migrated to SEPA', track_visibility='onchange',
            help="If this field is not active, the mandate section of the "
            "next direct debit file that include this mandate will contain "
            "the 'Original Mandate Identification' and the 'Original "
            "Creditor Scheme Identification'. This is required in a few "
            "countries (Belgium for instance), but not in all countries. "
            "If this is not required in your country, you should keep this "
            "field always active."),
        'original_mandate_identification': fields.char(
            'Original Mandate Identification', size=35,
            track_visibility='onchange',
            help="When the field 'Migrated to SEPA' is not active, this "
            "field will be used as the Original Mandate Identification in "
            "the Direct Debit file."),
        'scheme': fields.selection([
            ('CORE', 'Basic (CORE)'),
            ('B2B', 'Enterprise (B2B)')
            ], 'Scheme', required=True)
    }

    _defaults = {
        'sepa_migrated': True,
        'scheme': 'CORE',
    }

    def _check_sdd_mandate(self, cr, uid, ids):
        for mandate in self.browse(cr, uid, ids):
            if (mandate.type == 'recurrent' and
                    not mandate.recurrent_sequence_type):
                raise orm.except_orm(
                    _('Error:'),
                    _("The recurrent mandate '%s' must have a sequence type.")
                    % mandate.unique_mandate_reference)
            if (mandate.type == 'recurrent' and not mandate.sepa_migrated and
                    mandate.recurrent_sequence_type != 'first'):
                raise orm.except_orm(
                    _('Error:'),
                    _("The recurrent mandate '%s' which is not marked as "
                        "'Migrated to SEPA' must have its recurrent sequence "
                        "type set to 'First'.")
                    % mandate.unique_mandate_reference)
            if (mandate.type == 'recurrent' and not mandate.sepa_migrated and
                    not mandate.original_mandate_identification):
                raise orm.except_orm(
                    _('Error:'),
                    _("You must set the 'Original Mandate Identification' "
                        "on the recurrent mandate '%s' which is not marked "
                        "as 'Migrated to SEPA'.")
                    % mandate.unique_mandate_reference)
        return True

    _constraints = [
        (_check_sdd_mandate, "Error msg in raise", [
            'type', 'recurrent_sequence_type', 'sepa_migrated',
            'original_mandate_identification',
        ]),
    ]

    def create(self, cr, uid, vals, context=None):
        if vals.get('unique_mandate_reference', '/') == '/':
            vals['unique_mandate_reference'] = \
                self.pool['ir.sequence'].next_by_code(
                    cr, uid, 'sdd.mandate.reference', context=context)
        return super(sdd_mandate, self).create(cr, uid, vals, context=context)

    def mandate_type_change(self, cr, uid, ids, type):
        if type == 'recurrent':
            recurrent_sequence_type = 'first'
        else:
            recurrent_sequence_type = False
        res = {'value': {'recurrent_sequence_type': recurrent_sequence_type}}
        return res

    def mandate_partner_bank_change(
            self, cr, uid, ids, partner_bank_id, type, recurrent_sequence_type,
            last_debit_date, state):
        res = super(sdd_mandate, self).mandate_partner_bank_change(
            cr, uid, ids, partner_bank_id, last_debit_date, state)
        if (state == 'valid' and partner_bank_id and
                type == 'recurrent' and
                recurrent_sequence_type != 'first'):
            res['value']['recurrent_sequence_type'] = 'first'
            res['warning'] = {
                'title': _('Mandate update'),
                'message': _(
                    "As you changed the bank account attached to this "
                    "mandate, the 'Sequence Type' has been set back to "
                    "'First'."),
            }
        return res

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
