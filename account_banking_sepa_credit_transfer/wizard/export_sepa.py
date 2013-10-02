# -*- encoding: utf-8 -*-
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
import base64
from datetime import datetime, timedelta
from openerp.tools.translate import _
from openerp import tools, netsvc
from lxml import etree
import logging

_logger = logging.getLogger(__name__)


class banking_export_sepa_wizard(orm.TransientModel):
    _name = 'banking.export.sepa.wizard'
    _description = 'Export SEPA Credit Transfer XML file'
    _columns = {
        'state': fields.selection([('create', 'Create'), ('finish', 'Finish')],
            'State', readonly=True),
        'msg_identification': fields.char('Message identification', size=35,
            # Can't set required=True on the field because it blocks
            # the launch of the wizard -> I set it as required in the view
            help='This is the message identification of the entire SEPA XML file. 35 characters max.'),
        'batch_booking': fields.boolean('Batch booking',
            help="If true, the bank statement will display only one debit line for all the wire transfers of the SEPA XML file ; if false, the bank statement will display one debit line per wire transfer of the SEPA XML file."),
        'prefered_exec_date': fields.date('Prefered execution date',
            help='This is the date on which the file should be processed by the bank. Please keep in mind that banks only execute on working days and typically use a delay of two days between execution date and effective transfer date.'),
        'charge_bearer': fields.selection([
            ('SHAR', 'Shared'),
            ('CRED', 'Borne by creditor'),
            ('DEBT', 'Borne by debtor'),
            ('SLEV', 'Following service level'),
            ], 'Charge bearer', required=True,
            help='Shared : transaction charges on the sender side are to be borne by the debtor, transaction charges on the receiver side are to be borne by the creditor (most transfers use this). Borne by creditor : all transaction charges are to be borne by the creditor. Borne by debtor : all transaction charges are to be borne by the debtor. Following service level : transaction charges are to be applied following the rules agreed in the service level and/or scheme.'),
        'nb_transactions': fields.related('file_id', 'nb_transactions',
            type='integer', string='Number of transactions', readonly=True),
        'total_amount': fields.related('file_id', 'total_amount', type='float',
            string='Total amount', readonly=True),
        'file_id': fields.many2one('banking.export.sepa', 'SEPA XML file', readonly=True),
        'file': fields.related('file_id', 'file', string="File", type='binary',
            readonly=True),
        'filename': fields.related('file_id', 'filename', string="Filename",
            type='char', size=256, readonly=True),
        'payment_order_ids': fields.many2many('payment.order',
            'wiz_sepa_payorders_rel', 'wizard_id', 'payment_order_id',
            'Payment orders', readonly=True),
        }

    _defaults = {
        'charge_bearer': 'SLEV',
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
            raise orm.except_orm(_('Error :'), _("This IBAN is not valid : %s") % iban)

    def create(self, cr, uid, vals, context=None):
        payment_order_ids = context.get('active_ids', [])
        vals.update({
            'payment_order_ids': [[6, 0, payment_order_ids]],
        })
        return super(banking_export_sepa_wizard, self).create(cr, uid,
            vals, context=context)


    def create_sepa(self, cr, uid, ids, context=None):
        '''
        Creates the SEPA Credit Transfer file. That's the important code !
        '''
        sepa_export = self.browse(cr, uid, ids[0], context=context)

        my_company_name = sepa_export.payment_order_ids[0].mode.bank_id.partner_id.name
        my_company_iban = self._validate_iban(cr, uid, sepa_export.payment_order_ids[0].mode.bank_id.acc_number, context=context)
        my_company_bic = sepa_export.payment_order_ids[0].mode.bank_id.bank.bic
        #my_company_country_code = sepa_export.payment_order_ids[0].mode.bank_id.partner_id.address[0].country_id.code
        #my_company_city = sepa_export.payment_order_ids[0].mode.bank_id.partner_id.address[0].city
        #my_company_street1 = sepa_export.payment_order_ids[0].mode.bank_id.partner_id.address[0].street
        pain_flavor = sepa_export.payment_order_ids[0].mode.type.code
        if pain_flavor == 'pain.001.001.02':
            bic_xml_tag = 'BIC'
            name_maxsize = 70
            root_xml_tag = 'pain.001.001.02'
        elif pain_flavor == 'pain.001.001.03':
            bic_xml_tag = 'BIC'
            # size 70 -> 140 for <Nm> with pain.001.001.03
            # BUT the European Payment Council, in the document
            # "SEPA Credit Transfer Scheme Customer-to-bank Implementation guidelines" v6.0
            # available on http://www.europeanpaymentscouncil.eu/knowledge_bank.cfm
            # says that 'Nm' should be limited to 70
            # so we follow the "European Payment Council" and we put 70 and not 140
            name_maxsize = 70
            root_xml_tag = 'CstmrCdtTrfInitn'
        elif pain_flavor == 'pain.001.001.04':
            bic_xml_tag = 'BICFI'
            name_maxsize = 140
            root_xml_tag = 'CstmrCdtTrfInitn'
        else:
            raise orm.except_orm(_('Error :'), _("Payment Type Code '%s' is not supported. The only Payment Type Codes supported for SEPA Credit Transfers are 'pain.001.001.02', 'pain.001.001.03' and 'pain.001.001.04'.") % pain_flavor)
        if sepa_export.batch_booking:
            my_batch_booking = 'true'
        else:
            my_batch_booking = 'false'
        my_msg_identification = sepa_export.msg_identification
        if sepa_export.prefered_exec_date:
            my_requested_exec_date = sepa_export.prefered_exec_date
        else:
            my_requested_exec_date = datetime.strftime(datetime.today() + timedelta(days=1), '%Y-%m-%d')

        pain_ns = {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            None: 'urn:iso:std:iso:20022:tech:xsd:%s' % pain_flavor,
            }

        root = etree.Element('Document', nsmap=pain_ns)
        pain_root = etree.SubElement(root, root_xml_tag)
        # A. Group header
        group_header = etree.SubElement(pain_root, 'GrpHdr')
        message_identification = etree.SubElement(group_header, 'MsgId')
        message_identification.text = self._limit_size(cr, uid, my_msg_identification, 35, context=context)
        creation_date_time = etree.SubElement(group_header, 'CreDtTm')
        creation_date_time.text = datetime.strftime(datetime.today(), '%Y-%m-%dT%H:%M:%S')
        if pain_flavor == 'pain.001.001.02':
            # batch_booking is in "Group header" with pain.001.001.02
            # and in "Payment info" in pain.001.001.03/04
            batch_booking = etree.SubElement(group_header, 'BtchBookg')
            batch_booking.text = my_batch_booking
        nb_of_transactions_grphdr = etree.SubElement(group_header, 'NbOfTxs')
        control_sum_grphdr = etree.SubElement(group_header, 'CtrlSum')
        # Grpg removed in pain.001.001.03
        if pain_flavor == 'pain.001.001.02':
            grouping = etree.SubElement(group_header, 'Grpg')
            grouping.text = 'GRPD'
        initiating_party = etree.SubElement(group_header, 'InitgPty')
        initiating_party_name = etree.SubElement(initiating_party, 'Nm')
        initiating_party_name.text = self._limit_size(cr, uid, my_company_name, name_maxsize, context=context)
        # B. Payment info
        payment_info = etree.SubElement(pain_root, 'PmtInf')
        payment_info_identification = etree.SubElement(payment_info, 'PmtInfId')
        payment_info_identification.text = self._limit_size(cr, uid, my_msg_identification, 35, context=context)
        payment_method = etree.SubElement(payment_info, 'PmtMtd')
        payment_method.text = 'TRF'
        if pain_flavor in ['pain.001.001.03', 'pain.001.001.04']:
            # batch_booking is in "Group header" with pain.001.001.02
            # and in "Payment info" in pain.001.001.03/04
            batch_booking = etree.SubElement(payment_info, 'BtchBookg')
            batch_booking.text = my_batch_booking
        # It may seem surprising, but the
        # "SEPA Credit Transfer Scheme Customer-to-bank Implementation guidelines"
        # v6.0 says that control sum and nb_of_transactions should be present
        # at both "group header" level and "payment info" level
        # This seems to be confirmed by the tests carried out at
        # BNP Paribas in PAIN v001.001.03
        if pain_flavor in ['pain.001.001.03', 'pain.001.001.04']:
            nb_of_transactions_pmtinf = etree.SubElement(payment_info, 'NbOfTxs')
            control_sum_pmtinf = etree.SubElement(payment_info, 'CtrlSum')
        payment_type_info = etree.SubElement(payment_info, 'PmtTpInf')
        service_level = etree.SubElement(payment_type_info, 'SvcLvl')
        service_level_code = etree.SubElement(service_level, 'Cd')
        service_level_code.text = 'SEPA'
        requested_exec_date = etree.SubElement(payment_info, 'ReqdExctnDt')
        requested_exec_date.text = my_requested_exec_date
        debtor = etree.SubElement(payment_info, 'Dbtr')
        debtor_name = etree.SubElement(debtor, 'Nm')
        debtor_name.text = self._limit_size(cr, uid, my_company_name, name_maxsize, context=context)
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
        if my_company_bic:
            debtor_agent_bic = etree.SubElement(debtor_agent_institution, bic_xml_tag)
            debtor_agent_bic.text = my_company_bic
        charge_bearer = etree.SubElement(payment_info, 'ChrgBr')
        charge_bearer.text = sepa_export.charge_bearer

        transactions_count = 0
        total_amount = 0.0
        amount_control_sum = 0.0
        # Iterate on payment orders
        for payment_order in sepa_export.payment_order_ids:
            total_amount = total_amount + payment_order.total
            # Iterate each payment lines
            for line in payment_order.line_ids:
                transactions_count += 1
                # C. Credit Transfer Transaction Info
                credit_transfer_transaction_info = etree.SubElement(payment_info, 'CdtTrfTxInf')
                payment_identification = etree.SubElement(credit_transfer_transaction_info, 'PmtId')
                instruction_identification = etree.SubElement(payment_identification, 'InstrId')
                instruction_identification.text = self._limit_size(cr, uid, line.communication, 35, context=context) #otherwise, we can reach the invoice fields via ml_inv_ref
                end2end_identification = etree.SubElement(payment_identification, 'EndToEndId')
                end2end_identification.text = self._limit_size(cr, uid, line.communication, 35, context=context)
                amount = etree.SubElement(credit_transfer_transaction_info, 'Amt')
                instructed_amount = etree.SubElement(amount, 'InstdAmt', Ccy=line.currency.name)
                instructed_amount.text = '%.2f' % line.amount_currency
                amount_control_sum += line.amount_currency
                creditor_agent = etree.SubElement(credit_transfer_transaction_info, 'CdtrAgt')
                creditor_agent_institution = etree.SubElement(creditor_agent, 'FinInstnId')
                if not line.bank_id:
                    raise orm.except_orm(_('Error :'), _("Missing Bank Account on invoice '%s' (payment order line reference '%s').") %(line.ml_inv_ref.number, line.name))
                if line.bank_id.bank.bic:
                    creditor_agent_bic = etree.SubElement(creditor_agent_institution, bic_xml_tag)
                    creditor_agent_bic.text = line.bank_id.bank.bic
                creditor = etree.SubElement(credit_transfer_transaction_info, 'Cdtr')
                creditor_name = etree.SubElement(creditor, 'Nm')
                creditor_name.text = self._limit_size(cr, uid, line.partner_id.name, name_maxsize, context=context)
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
                creditor_account_iban.text = self._validate_iban(cr, uid, line.bank_id.acc_number, context=context)
                remittance_info = etree.SubElement(credit_transfer_transaction_info, 'RmtInf')
                # switch to Structured (Strdr) ? If we do it, beware that the format is not the same between pain 02 and pain 03
                remittance_info_unstructured = etree.SubElement(remittance_info, 'Ustrd')
                remittance_info_unstructured.text = self._limit_size(cr, uid, line.communication, 140, context=context)

        if pain_flavor in ['pain.001.001.03', 'pain.001.001.04']:
            nb_of_transactions_grphdr.text = nb_of_transactions_pmtinf.text = str(transactions_count)
            control_sum_grphdr.text = control_sum_pmtinf.text = '%.2f' % amount_control_sum
        else:
            nb_of_transactions_grphdr.text = str(transactions_count)
            control_sum_grphdr.text = '%.2f' % amount_control_sum


        xml_string = etree.tostring(root, pretty_print=True, encoding='UTF-8', xml_declaration=True)
        _logger.debug("Generated SEPA XML file below")
        _logger.debug(xml_string)
        official_pain_schema = etree.XMLSchema(etree.parse(tools.file_open('account_banking_sepa_credit_transfer/data/%s.xsd' % pain_flavor)))

        try:
            root_to_validate = etree.fromstring(xml_string)
            official_pain_schema.assertValid(root_to_validate)
        except Exception, e:
            _logger.warning("The XML file is invalid against the XML Schema Definition")
            _logger.warning(xml_string)
            _logger.warning(e)
            raise orm.except_orm(_('Error :'), _('The generated XML file is not valid against the official XML Schema Definition. The generated XML file and the full error have been written in the server logs. Here is the error, which may give you an idea on the cause of the problem : %s') % str(e))

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

        self.write(cr, uid, ids, {
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
        Save the SEPA PAIN: send the done signal to all payment orders in the file.
        With the default workflow, they will transition to 'done', while with the
        advanced workflow in account_banking_payment they will transition to 'sent'
        waiting reconciliation.
        '''
        sepa_export = self.browse(cr, uid, ids[0], context=context)
        self.pool.get('banking.export.sepa').write(cr, uid,
            sepa_export.file_id.id, {'state': 'sent'}, context=context)
        wf_service = netsvc.LocalService('workflow')
        for order in sepa_export.payment_order_ids:
            wf_service.trg_validate(uid, 'payment.order', order.id, 'done', cr)
        return {'type': 'ir.actions.act_window_close'}
