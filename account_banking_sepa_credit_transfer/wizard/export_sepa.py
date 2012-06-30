# -*- encoding: utf-8 -*-
##############################################################################
#
#    SEPA Credit Transfer module for OpenERP
#    Copyright (C) 2010-2012 Akretion (http://www.akretion.com)
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

# TODO :
# What about if we have to pay 2 invoices for the same supplier
# -> creates 2 payment lines :-(

from osv import osv, fields
import base64
from datetime import datetime, date, timedelta
from tools.translate import _
from lxml import etree
import decimal_precision as dp
import logging
import netsvc # not for logs, but for workflow
import pain_001_001_04_xsd

_logger = logging.getLogger(__name__)


class banking_export_sepa_wizard(osv.osv_memory):
    _name = 'banking.export.sepa.wizard'
    _description = 'Export SEPA Credit Transfer XML file'
    _columns = {
        'state': fields.selection([('create', 'Create'), ('finish', 'Finish')],
            'State', readonly=True),
        'msg_identification': fields.char('Message identification', size=35,
            required=True,
            help='This is the message identification of the full SEPA XML file. 35 characters max.'),
        'batch_booking': fields.boolean('Batch booking',
            help="If true, the bank statement will display only one debit line for all the wire transfers of the PAIN file ; if false, the bank statement will display one debit line per wire transfer of the PAIN file."),
        'prefered_exec_date': fields.date('Prefered execution date',
            help='This is the date the file should be processed by the bank. Please keep in mind that banks only execute on working days and typically use a delay of two days between execution date and effective transfer date.'),
        'charge_bearer': fields.selection([
            ('SHAR', 'Shared'),
            ('CRED', 'Borne by creditor'),
            ('DEBT', 'Borne by debtor'),
            ('SLEV', 'Following service level'),
            ], 'Charge bearer', required=True,
            help='Shared : transaction charges on the sender side are to be borne by the debtor, transaction charges on the receiver side are to be borne by the creditor (this is the default ; most transfers use this). Borne by creditor : all transaction charges are to be borne by the creditor. Borne by debtor : all transaction charges are to be borne by the debtor. Following service level : transaction charges are to be applied following the rules agreed in the service level and/or scheme.'),
        'nb_transactions': fields.related('file_id', 'nb_transactions',
            type='integer', string='Number of transactions', readonly=True),
        'total_amount': fields.related('file_id', 'total_amount', type='float',
            string='Total Amount', readonly=True),
        'file_id': fields.many2one('banking.export.sepa', 'SEPA XML file', readonly=True),
        'file': fields.related('file_id', 'file', string="File", type='binary',
            readonly=True),
        'payment_order_ids': fields.many2many('payment.order',
            'wiz_sepa_payorders_rel', 'wizard_id', 'payment_order_id',
            'Payment orders', readonly=True),
        }

    _defaults = {
        'charge_bearer': 'SHAR',
        'state': 'create',
        }


    def _limit_size(self, cr, uid, field, max_size, context=None):
        '''Limit size of strings to respect the PAIN standard'''
        max_size = int(max_size)
        return field[0:max_size]


    def _validate_iban(self, cr, uid, iban, context=None):
        '''if IBAN is valid, returns IBAN
        if IBAN is NOT valid, raises an error message'''
        partner_bank_obj = self.pool.get('res.partner.bank')
        if partner_bank_obj.is_iban_valid(cr, uid, iban, context=context):
            return iban.replace(' ', '')
        else:
            raise osv.except_osv(_('Error :'), _("This IBAN is not valid : %s" % iban))

    def create(self, cr, uid, vals, context=None):
        self.check_orders(cr, uid, vals, context=context)
        return super(banking_export_sepa_wizard, self).create(cr, uid,
            vals, context=context)

    def check_orders(self, cr, uid, vals, context=None):
        payment_order_ids = context.get('active_ids')
        # TODO : finish this code
        #runs = {}
        #for payment_order in self.pool.get('payment.order').browse(cr, uid, payment_order_ids, context=context):
        #    payment_type = payment_order.mode.type.code
        #    if payment_type in runs:
        #        runs[payment_type].append(payment_order)
        #    else:
        #        runs[payment_type] = [payment_order]
        vals.update({
            'payment_order_ids': [[6, 0, payment_order_ids]],
        })


    def create_sepa(self, cr, uid, ids, context=None):
        '''
        Creates the SEPA Credit Transfer file. That's the important code !
        '''
        payment_order_obj = self.pool.get('payment.order')

        sepa_export = self.browse(cr, uid, ids[0], context=context)

        pain_ns = {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            None: 'urn:iso:std:iso:20022:tech:xsd:pain.001.001.04',
            }

        my_company_name = sepa_export.payment_order_ids[0].mode.bank_id.partner_id.name
        my_company_iban = self._validate_iban(cr, uid, sepa_export.payment_order_ids[0].mode.bank_id.iban, context=context)
        my_company_bic = sepa_export.payment_order_ids[0].mode.bank_id.bank.bic
        my_company_country_code = sepa_export.payment_order_ids[0].mode.bank_id.partner_id.address[0].country_id.code
        my_company_city = sepa_export.payment_order_ids[0].mode.bank_id.partner_id.address[0].city
        my_company_street1 = sepa_export.payment_order_ids[0].mode.bank_id.partner_id.address[0].street
        if sepa_export.batch_booking:
            my_batch_booking = 'true'
        else:
            my_batch_booking = 'false'
        my_msg_identification = sepa_export.msg_identification
        if sepa_export.prefered_exec_date:
            my_requested_exec_date = sepa_export.prefered_exec_date
        else:
            my_requested_exec_date = datetime.strftime(datetime.today() + timedelta(days=1), '%Y-%m-%d')

        root = etree.Element('Document', nsmap=pain_ns)
        pain_root = etree.SubElement(root, 'CstmrCdtTrfInitn')
        # A. Group header
        group_header = etree.SubElement(pain_root, 'GrpHdr')
        message_identification = etree.SubElement(group_header, 'MsgId')
        message_identification.text = self._limit_size(cr, uid, my_msg_identification, 35, context=context)
        creation_date_time = etree.SubElement(group_header, 'CreDtTm')
        creation_date_time.text = datetime.strftime(datetime.today(), '%Y-%m-%dT%H:%M:%S')
        nb_of_transactions = etree.SubElement(group_header, 'NbOfTxs')
        control_sum = etree.SubElement(group_header, 'CtrlSum')
        # Grpg removed in pain.001.001.03
        #grouping = etree.SubElement(group_header, 'Grpg')
        #grouping.text = 'GRPD'
        initiating_party = etree.SubElement(group_header, 'InitgPty')
        initiating_party_name = etree.SubElement(initiating_party, 'Nm')
        initiating_party_name.text = self._limit_size(cr, uid, my_company_name, 70, context=context)
        # B. Payment info
        payment_info = etree.SubElement(pain_root, 'PmtInf')
        payment_info_identification = etree.SubElement(payment_info, 'PmtInfId')
        payment_info_identification.text = self._limit_size(cr, uid, my_msg_identification, 35, context=context)
        payment_method = etree.SubElement(payment_info, 'PmtMtd')
        payment_method.text = 'TRF'
        batch_booking = etree.SubElement(payment_info, 'BtchBookg') # Was in "Group header with pain.001.001.02
        batch_booking.text = my_batch_booking
        requested_exec_date = etree.SubElement(payment_info, 'ReqdExctnDt')
        requested_exec_date.text = my_requested_exec_date
        debtor = etree.SubElement(payment_info, 'Dbtr')
        debtor_name = etree.SubElement(debtor, 'Nm')
        debtor_name.text = self._limit_size(cr, uid, my_company_name, 140, context=context) # size 70 -> 140 with pain.001.001.03
#        debtor_address = etree.SubElement(debtor, 'PstlAdr')
#        debtor_street = etree.SubElement(debtor_address, 'AdrLine')
#        debtor_street.text = my_company_street1
#        debtor_city = etree.SubElement(debtor_address, 'AdrLine')
#        debtor_city.text = my_company_city
#        debtor_country = etree.SubElement(debtor_address, 'Ctry')
#        debtor_country.text = my_company_country_code
        debtor_account = etree.SubElement(payment_info, 'DbtrAcct')
        debtor_account_id = etree.SubElement(debtor_account, 'Id')
        debtor_account_iban = etree.SubElement(debtor_account_id, 'IBAN')
        debtor_account_iban.text = my_company_iban
        debtor_agent = etree.SubElement(payment_info, 'DbtrAgt')
        debtor_agent_institution = etree.SubElement(debtor_agent, 'FinInstnId')
        debtor_agent_bic = etree.SubElement(debtor_agent_institution, 'BIC')
        debtor_agent_bic.text = my_company_bic

        transactions_count = 0
        total_amount = 0.0
        # Iterate on payment orders
        for payment_order in sepa_export.payment_order_ids:
            total_amount = total_amount + payment_order.total
            # Iterate each payment lines
            for line in payment_order.line_ids:
                transactions_count = transactions_count + 1
                # C. Credit Transfer Transaction Info
                credit_transfer_transaction_info = etree.SubElement(payment_info, 'CdtTrfTxInf')
                payment_identification = etree.SubElement(credit_transfer_transaction_info, 'PmtId')
                instruction_identification = etree.SubElement(payment_identification, 'InstrId')
                instruction_identification.text = self._limit_size(cr, uid, line.communication, 35, context=context) #otherwise, we can reach the invoice fields via ml_inv_ref
                end2end_identification = etree.SubElement(payment_identification, 'EndToEndId')
                end2end_identification.text = self._limit_size(cr, uid, line.communication, 35, context=context)
                amount = etree.SubElement(credit_transfer_transaction_info, 'Amt')
                instructed_amount = etree.SubElement(amount, 'InstdAmt', Ccy=line.company_currency.name)
                instructed_amount.text = '%.2f' % line.amount
                charge_bearer = etree.SubElement(credit_transfer_transaction_info, 'ChrgBr')
                charge_bearer.text = sepa_export.charge_bearer
                creditor_agent = etree.SubElement(credit_transfer_transaction_info, 'CdtrAgt')
                creditor_agent_institution = etree.SubElement(creditor_agent, 'FinInstnId')
                creditor_agent_bic = etree.SubElement(creditor_agent_institution, 'BIC')
                creditor_agent_bic.text = line.bank_id.bank.bic
                creditor = etree.SubElement(credit_transfer_transaction_info, 'Cdtr')
                creditor_name = etree.SubElement(creditor, 'Nm')
                creditor_name.text = self._limit_size(cr, uid, line.partner_id.name, 140, context=context) # size 70 -> 140 with pain.001.001.03
# I don't think they want it
# If they want it, we need to implement full spec p26 appendix
#                creditor_address = etree.SubElement(creditor, 'PstlAdr')
#                creditor_street = etree.SubElement(creditor_address, 'AdrLine')
#                creditor_street.text = line.partner_id.address[0].street
#                creditor_city = etree.SubElement(creditor_address, 'AdrLine')
#                creditor_city.text = line.partner_id.address[0].city
#                creditor_country = etree.SubElement(creditor_address, 'Ctry')
#                creditor_country.text = line.partner_id.address[0].country_id.code
                creditor_account = etree.SubElement(credit_transfer_transaction_info, 'CdtrAcct')
                creditor_account_id = etree.SubElement(creditor_account, 'Id')
                creditor_account_iban = etree.SubElement(creditor_account_id, 'IBAN')
                creditor_account_iban.text = self._validate_iban(cr, uid, line.bank_id.iban, context=context)
                remittance_info = etree.SubElement(credit_transfer_transaction_info, 'RmtInf')
                # TODO : switch to Structured RmtInf ?
                remittance_info_unstructured = etree.SubElement(remittance_info, 'Ustrd')
                remittance_info_unstructured.text = self._limit_size(cr, uid, line.communication, 140, context=context)

        nb_of_transactions.text = str(transactions_count)
        control_sum.text = '%.2f' % total_amount

        xml_string = etree.tostring(root, pretty_print=True, encoding='UTF-8', xml_declaration=True)
        _logger.debug("Generated SEPA XML file below")
        _logger.debug(xml_string)
        official_pain_schema = etree.XMLSchema(etree.fromstring(pain_001_001_04_xsd.pain_001_001_04_xsd))

# TODO make XSD validation work !
#        try:
#            official_pain_schema.assertValid(root)
#        except Exception, e:
#            _logger.warning("The XML file is invalid against the XML Schema Definition")
#            _logger.warning(xml_string)
#            _logger.warning(e)
#            raise osv.except_osv(_('Error :'), _('The generated XML file is not valid against the official XML Schema Definition. The generated XML file and the full error have been written in the server logs. Here is the error, which may give you an idea on the cause of the problem : %s') % str(e))

        # CREATE the banking.export.sepa record
        file_id = self.pool.get('banking.export.sepa').create(cr, uid,
            {
            'msg_identification': my_msg_identification,
            'batch_booking': sepa_export.batch_booking,
            'charge_bearer': sepa_export.charge_bearer,
            'prefered_exec_date': sepa_export.prefered_exec_date,
            'total_amount': total_amount,
            'nb_transactions': transactions_count,
            'file': base64.encodestring(xml_string),
            'payment_order_ids': [
                (6, 0, [x.id for x in sepa_export.payment_order_ids])
            ],
            }, context=context)

        self.write(cr, uid, ids[0], {
            'file_id': file_id,
            'state': 'finish',
            }, context=context)

        action = {
            'name': 'SEPA XML',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': self._name,
            'res_id': ids[0],
            'target': 'new',
            }
        return action


    def cancel_sepa(self, cr, uid, ids, context=None):
        '''
        Cancel the SEPA PAIN: just drop the file
        '''
        sepa_export = self.browse(cr, uid, ids[0], context=context)
        self.pool.get('banking.export.sepa').unlink(cr, uid, sepa_export.file_id.id, context=context)
        return {'type': 'ir.actions.act_window_close'}


    def save_sepa(self, cr, uid, ids, context=None):
        '''
        Save the SEPA PAIN: mark all payments in the file as 'sent'.
        '''
        sepa_export = self.browse(cr, uid, ids[0], context=context)
        sepa_file = self.pool.get('banking.export.sepa').write(cr, uid,
            sepa_export.file_id.id, {'state': 'sent'}, context=context)
        wf_service = netsvc.LocalService('workflow')
        for order in sepa_export.payment_order_ids:
            wf_service.trg_validate(uid, 'payment.order', order.id, 'sent', cr)
        return {'type': 'ir.actions.act_window_close'}


banking_export_sepa_wizard()

