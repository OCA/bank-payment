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


class banking_export_sdd(orm.Model):
    '''SEPA Direct Debit export'''
    _name = 'banking.export.sdd'
    _description = __doc__
    _rec_name = 'msg_identification'

    def _generate_filename(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for sepa_file in self.browse(cr, uid, ids, context=context):
            res[sepa_file.id] = 'sdd_' + (sepa_file.msg_identification or '') + '.xml'
        return res

    _columns = {
        'payment_order_ids': fields.many2many(
            'payment.order',
            'account_payment_order_sdd_rel',
            'banking_export_sepa_id', 'account_order_id',
            'Payment orders',
            readonly=True),
        'requested_collec_date': fields.date('Requested collection date', readonly=True),
        'nb_transactions': fields.integer('Number of transactions', readonly=True),
        'total_amount': fields.float('Total amount',
            digits_compute=dp.get_precision('Account'), readonly=True),
        'msg_identification': fields.char('Message identification', size=35,
            readonly=True),
        'batch_booking': fields.boolean('Batch booking', readonly=True,
            help="If true, the bank statement will display only one credit line for all the direct debits of the SEPA XML file ; if false, the bank statement will display one credit line per direct debit of the SEPA XML file."),
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
        'generation_date': fields.date.context_today,
        'state': 'draft',
    }


class sdd_mandate(orm.Model):
    '''SEPA Direct Debit Mandate'''
    _name = 'sdd.mandate'
    _description = __doc__
    _rec_name = 'unique_mandate_reference'
    _order = 'signature_date desc'

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
        'last_debit_date': fields.date('Date of the Last Debit',
            help="For recurrent mandates, this field is used to know if the SDD will be of type 'First' or 'Recurring'. For one-off mandates, this field is used to know if the SDD has already been used or not."),
        'state': fields.selection([
            ('valid', 'Valid'),
            ('expired', 'Expired'),
            ], 'Mandate Status',
            help="For a recurrent mandate, this field indicate if the mandate is still valid or if it has expired (a recurrent mandate expires if it's not used during 36 months). For a one-off mandate, it expires after its first use."),
        }

    _sql_constraints = [(
        'mandate_ref_company_uniq',
        'unique(unique_mandate_reference, company_id)',
        'A Mandate with the same reference already exists for this company !'
        )]

    _defaults = {
        'company_id': lambda self, cr, uid, context: \
            self.pool['res.users'].browse(cr, uid, uid, context=context).\
                company_id.id,
        'unique_mandate_reference': lambda self, cr, uid, context: \
            self.pool['ir.sequence'].get(cr, uid, 'sdd.mandate.reference'),
        'state': 'valid',
    }


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

    def _check_sdd_mandate(self, cr, uid, ids):
        for payline in self.browse(cr, uid, ids):
            if payline.sdd_mandate_id and not payline.bank_id:
                raise orm.except_orm(
                    _('Error :'),
                    _("Missing bank account on the payment line with SEPA\
                    Direct Debit Mandate '%s'."
                    % payline.sdd_mandate_id.unique_mandate_reference))
            elif payline.sdd_mandate_id and payline.bank_id and payline.sdd_mandate_id.partner_bank_id != payline.bank_id.id:
                raise orm.except_orm(
                    _('Error :'),
                    _("The SEPA Direct Debit Mandate '%s' is not related??"))

        return True

#    _constraints = [
#        (_check_sdd_mandate, "Mandate must be attached to bank account", ['bank_id', 'sdd_mandate_id']),
#    ]

    # TODO inherit create to select the first mandate ??
