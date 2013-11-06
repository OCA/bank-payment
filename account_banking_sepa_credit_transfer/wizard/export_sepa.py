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
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval
from openerp import tools, netsvc
from lxml import etree
import logging
from unidecode import unidecode

_logger = logging.getLogger(__name__)


class banking_export_sepa_wizard(orm.TransientModel):
    _name = 'banking.export.sepa.wizard'
    _description = 'Export SEPA Credit Transfer File'

    _columns = {
        'state': fields.selection([
            ('create', 'Create'),
            ('finish', 'Finish'),
            ], 'State', readonly=True),
        'batch_booking': fields.boolean(
            'Batch Booking',
            help="If true, the bank statement will display only one debit line for all the wire transfers of the SEPA XML file ; if false, the bank statement will display one debit line per wire transfer of the SEPA XML file."),
        'prefered_exec_date': fields.date(
            'Prefered Execution Date',
            help='This is the date on which the file should be processed by the bank. Please keep in mind that banks only execute on working days and typically use a delay of two days between execution date and effective transfer date.'),
        'charge_bearer': fields.selection([
            ('SLEV', 'Following Service Level'),
            ('SHAR', 'Shared'),
            ('CRED', 'Borne by Creditor'),
            ('DEBT', 'Borne by Debtor'),
            ], 'Charge Bearer', required=True,
            help='Following service level : transaction charges are to be applied following the rules agreed in the service level and/or scheme (SEPA Core messages must use this). Shared : transaction charges on the debtor side are to be borne by the debtor, transaction charges on the creditor side are to be borne by the creditor. Borne by creditor : all transaction charges are to be borne by the creditor. Borne by debtor : all transaction charges are to be borne by the debtor.'),
        'nb_transactions': fields.related(
            'file_id', 'nb_transactions', type='integer',
            string='Number of Transactions', readonly=True),
        'total_amount': fields.related(
            'file_id', 'total_amount', type='float', string='Total Amount',
            readonly=True),
        'file_id': fields.many2one(
            'banking.export.sepa', 'SEPA XML File', readonly=True),
        'file': fields.related(
            'file_id', 'file', string="File", type='binary', readonly=True),
        'filename': fields.related(
            'file_id', 'filename', string="Filename", type='char',
            size=256, readonly=True),
        'payment_order_ids': fields.many2many(
            'payment.order', 'wiz_sepa_payorders_rel', 'wizard_id',
            'payment_order_id', 'Payment Orders', readonly=True),
        }

    _defaults = {
        'charge_bearer': 'SLEV',
        'state': 'create',
        }

    def _validate_iban(self, cr, uid, iban, context=None):
        '''if IBAN is valid, returns IBAN
        if IBAN is NOT valid, raises an error message'''
        partner_bank_obj = self.pool.get('res.partner.bank')
        if partner_bank_obj.is_iban_valid(cr, uid, iban, context=context):
            return iban.replace(' ', '')
        else:
            raise orm.except_orm(
                _('Error:'), _("This IBAN is not valid : %s") % iban)

    def create(self, cr, uid, vals, context=None):
        payment_order_ids = context.get('active_ids', [])
        vals.update({
            'payment_order_ids': [[6, 0, payment_order_ids]],
        })
        return super(banking_export_sepa_wizard, self).create(
            cr, uid, vals, context=context)

    def _prepare_field(
            self, cr, uid, field_name, field_value, max_size=0,
            sepa_export=False, line=False, context=None):
        '''This function is designed to be inherited !'''
        eval_ctx = {
            'sepa_export': sepa_export,
            'line': line,
            }
        try:
            # SEPA uses XML ; XML = UTF-8 ; UTF-8 = support for all characters
            # But we are dealing with banks...
            # and many banks don't want non-ASCCI characters !
            # cf section 1.4 "Character set" of the SEPA Credit Transfer
            # Scheme Customer-to-bank guidelines
            value = unidecode(safe_eval(field_value, eval_ctx))
        except:
            if line:
                raise orm.except_orm(
                    _('Error:'),
                    _("Cannot compute the '%s' of the Payment Line with Invoice Reference '%s'.")
                    % (field_name, self.pool['account.invoice'].name_get(cr, uid, [line.ml_inv_ref.id], context=context)[0][1]))
            else:
                raise orm.except_orm(
                    _('Error:'),
                    _("Cannot compute the '%s'.") % field_name)
        if not isinstance(value, (str, unicode)):
            raise orm.except_orm(
                _('Field type error:'),
                _("The type of the field '%s' is %s. It should be a string or unicode.")
                % (field_name, type(value)))
        if not value:
            raise orm.except_orm(
                _('Error:'),
                _("The '%s' is empty or 0. It should have a non-null value.")
                % field_name)
        if max_size and len(value) > max_size:
            value = value[0:max_size]
        return value

    def _prepare_export_sepa(
            self, cr, uid, sepa_export, total_amount, transactions_count,
            xml_string, context=None):
        return {
            'batch_booking': sepa_export.batch_booking,
            'charge_bearer': sepa_export.charge_bearer,
            'prefered_exec_date': sepa_export.prefered_exec_date,
            'total_amount': total_amount,
            'nb_transactions': transactions_count,
            'file': base64.encodestring(xml_string),
            'payment_order_ids': [
                (6, 0, [x.id for x in sepa_export.payment_order_ids])
            ],
        }

    def _validate_xml(self, cr, uid, xml_string, pain_flavor):
        xsd_etree_obj = etree.parse(
            tools.file_open(
                'account_banking_sepa_credit_transfer/data/%s.xsd'
                % pain_flavor))
        official_pain_schema = etree.XMLSchema(xsd_etree_obj)

        try:
            root_to_validate = etree.fromstring(xml_string)
            official_pain_schema.assertValid(root_to_validate)
        except Exception, e:
            _logger.warning(
                "The XML file is invalid against the XML Schema Definition")
            _logger.warning(xml_string)
            _logger.warning(e)
            raise orm.except_orm(
                _('Error:'),
                _('The generated XML file is not valid against the official XML Schema Definition. The generated XML file and the full error have been written in the server logs. Here is the error, which may give you an idea on the cause of the problem : %s')
                % str(e))
        return True

    def create_sepa(self, cr, uid, ids, context=None):
        '''
        Creates the SEPA Credit Transfer file. That's the important code !
        '''
        sepa_export = self.browse(cr, uid, ids[0], context=context)
        pain_flavor = sepa_export.payment_order_ids[0].mode.type.code
        if pain_flavor == 'pain.001.001.02':
            bic_xml_tag = 'BIC'
            name_maxsize = 70
            root_xml_tag = 'pain.001.001.02'
        elif pain_flavor == 'pain.001.001.03':
            bic_xml_tag = 'BIC'
            # size 70 -> 140 for <Nm> with pain.001.001.03
            # BUT the European Payment Council, in the document
            # "SEPA Credit Transfer Scheme Customer-to-bank
            # Implementation guidelines" v6.0 available on
            # http://www.europeanpaymentscouncil.eu/knowledge_bank.cfm
            # says that 'Nm' should be limited to 70
            # so we follow the "European Payment Council"
            # and we put 70 and not 140
            name_maxsize = 70
            root_xml_tag = 'CstmrCdtTrfInitn'
        elif pain_flavor == 'pain.001.001.04':
            bic_xml_tag = 'BICFI'
            name_maxsize = 140
            root_xml_tag = 'CstmrCdtTrfInitn'
        elif pain_flavor == 'pain.001.001.05':
            bic_xml_tag = 'BICFI'
            name_maxsize = 140
            root_xml_tag = 'CstmrCdtTrfInitn'

        else:
            raise orm.except_orm(
                _('Error:'),
                _("Payment Type Code '%s' is not supported. The only Payment Type Codes supported for SEPA Credit Transfers are 'pain.001.001.02', 'pain.001.001.03', 'pain.001.001.04' and 'pain.001.001.05'.")
                % pain_flavor)
        if sepa_export.prefered_exec_date:
            my_requested_exec_date = sepa_export.prefered_exec_date
        else:
            my_requested_exec_date = fields.date.context_today(
                self, cr, uid, context=context)

        pain_ns = {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            None: 'urn:iso:std:iso:20022:tech:xsd:%s' % pain_flavor,
            }

        root = etree.Element('Document', nsmap=pain_ns)
        pain_root = etree.SubElement(root, root_xml_tag)

        my_company_name = self._prepare_field(
            cr, uid, 'Company Name',
            'sepa_export.payment_order_ids[0].mode.bank_id.partner_id.name',
            name_maxsize, sepa_export=sepa_export, context=context)

        # A. Group header
        group_header_1_0 = etree.SubElement(pain_root, 'GrpHdr')
        message_identification_1_1 = etree.SubElement(
            group_header_1_0, 'MsgId')
        message_identification_1_1.text = self._prepare_field(
            cr, uid, 'Message Identification',
            'sepa_export.payment_order_ids[0].reference', 35,
            sepa_export=sepa_export, context=context)
        creation_date_time_1_2 = etree.SubElement(group_header_1_0, 'CreDtTm')
        creation_date_time_1_2.text = datetime.strftime(
            datetime.today(), '%Y-%m-%dT%H:%M:%S')
        if pain_flavor == 'pain.001.001.02':
            # batch_booking is in "Group header" with pain.001.001.02
            # and in "Payment info" in pain.001.001.03/04
            batch_booking = etree.SubElement(group_header_1_0, 'BtchBookg')
            batch_booking.text = str(sepa_export.batch_booking).lower()
        nb_of_transactions_1_6 = etree.SubElement(
            group_header_1_0, 'NbOfTxs')
        control_sum_1_7 = etree.SubElement(group_header_1_0, 'CtrlSum')
        # Grpg removed in pain.001.001.03
        if pain_flavor == 'pain.001.001.02':
            grouping = etree.SubElement(group_header_1_0, 'Grpg')
            grouping.text = 'GRPD'
        initiating_party_1_8 = etree.SubElement(group_header_1_0, 'InitgPty')
        initiating_party_name = etree.SubElement(initiating_party_1_8, 'Nm')
        initiating_party_name.text = my_company_name

        # B. Payment info
        payment_info_2_0 = etree.SubElement(pain_root, 'PmtInf')
        payment_info_identification_2_1 = etree.SubElement(
            payment_info_2_0, 'PmtInfId')
        payment_info_identification_2_1.text = self._prepare_field(
            cr, uid, 'Payment Information Identification',
            "sepa_export.payment_order_ids[0].reference",
            35, sepa_export=sepa_export, context=context)
        payment_method_2_2 = etree.SubElement(payment_info_2_0, 'PmtMtd')
        payment_method_2_2.text = 'TRF'
        if pain_flavor in [
                'pain.001.001.03', 'pain.001.001.04', 'pain.001.001.05']:
            # batch_booking is in "Group header" with pain.001.001.02
            # and in "Payment info" in pain.001.001.03/04
            batch_booking_2_3 = etree.SubElement(payment_info_2_0, 'BtchBookg')
            batch_booking_2_3.text = str(sepa_export.batch_booking).lower()
        # It may seem surprising, but the
        # "SEPA Credit Transfer Scheme Customer-to-bank Implementation
        # guidelines" v6.0 says that control sum and nb_of_transactions
        # should be present at both "group header" level and "payment info"
        # level. This seems to be confirmed by the tests carried out at
        # BNP Paribas in PAIN v001.001.03
        if pain_flavor in [
                'pain.001.001.03', 'pain.001.001.04', 'pain.001.001.05']:
            nb_of_transactions_2_4 = etree.SubElement(
                payment_info_2_0, 'NbOfTxs')
            control_sum_2_5 = etree.SubElement(payment_info_2_0, 'CtrlSum')
        payment_type_info_2_6 = etree.SubElement(payment_info_2_0, 'PmtTpInf')
        service_level_2_8 = etree.SubElement(payment_type_info_2_6, 'SvcLvl')
        service_level_code_2_9 = etree.SubElement(service_level_2_8, 'Cd')
        service_level_code_2_9.text = 'SEPA'
        requested_exec_date_2_17 = etree.SubElement(
            payment_info_2_0, 'ReqdExctnDt')
        requested_exec_date_2_17.text = my_requested_exec_date
        debtor_2_19 = etree.SubElement(payment_info_2_0, 'Dbtr')
        debtor_name = etree.SubElement(debtor_2_19, 'Nm')
        debtor_name.text = my_company_name
        debtor_account_2_20 = etree.SubElement(payment_info_2_0, 'DbtrAcct')
        debtor_account_id = etree.SubElement(debtor_account_2_20, 'Id')
        debtor_account_iban = etree.SubElement(debtor_account_id, 'IBAN')
        debtor_account_iban.text = self._validate_iban(
            cr, uid, self._prepare_field(
                cr, uid, 'Company IBAN',
                'sepa_export.payment_order_ids[0].mode.bank_id.acc_number',
                sepa_export=sepa_export, context=context),
            context=context)
        debtor_agent_2_21 = etree.SubElement(payment_info_2_0, 'DbtrAgt')
        debtor_agent_institution = etree.SubElement(
            debtor_agent_2_21, 'FinInstnId')
        debtor_agent_bic = etree.SubElement(
            debtor_agent_institution, bic_xml_tag)
        # TODO validate BIC with pattern
        # [A-Z]{6,6}[A-Z2-9][A-NP-Z0-9]([A-Z0-9]{3,3}){0,1}
        # because OpenERP doesn't have a constraint on BIC
        debtor_agent_bic.text = self._prepare_field(
            cr, uid, 'Company BIC',
            'sepa_export.payment_order_ids[0].mode.bank_id.bank.bic',
            sepa_export=sepa_export, context=context)
        charge_bearer_2_24 = etree.SubElement(payment_info_2_0, 'ChrgBr')
        charge_bearer_2_24.text = sepa_export.charge_bearer

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
                credit_transfer_transaction_info_2_27 = etree.SubElement(
                    payment_info_2_0, 'CdtTrfTxInf')
                payment_identification_2_28 = etree.SubElement(
                    credit_transfer_transaction_info_2_27, 'PmtId')
                end2end_identification_2_30 = etree.SubElement(
                    payment_identification_2_28, 'EndToEndId')
                end2end_identification_2_30.text = self._prepare_field(
                    cr, uid, 'End to End Identification', 'line.name', 35,
                    line=line, context=context)
                currency_name = self._prepare_field(
                    cr, uid, 'Currency Code', 'line.currency.name', 3,
                    line=line, context=context)
                amount_2_42 = etree.SubElement(
                    credit_transfer_transaction_info_2_27, 'Amt')
                instructed_amount_2_43 = etree.SubElement(
                    amount_2_42, 'InstdAmt', Ccy=currency_name)
                instructed_amount_2_43.text = '%.2f' % line.amount_currency
                amount_control_sum += line.amount_currency
                creditor_agent_2_77 = etree.SubElement(
                    credit_transfer_transaction_info_2_27, 'CdtrAgt')
                creditor_agent_institution = etree.SubElement(
                    creditor_agent_2_77, 'FinInstnId')
                if not line.bank_id:
                    raise orm.except_orm(
                        _('Error:'),
                        _("Missing Bank Account on invoice '%s' (payment order line reference '%s').")
                        % (line.ml_inv_ref.number, line.name))
                creditor_agent_bic = etree.SubElement(
                    creditor_agent_institution, bic_xml_tag)
                creditor_agent_bic.text = self._prepare_field(
                    cr, uid, 'Customer BIC', 'line.bank_id.bank.bic',
                    line=line, context=context)
                creditor_2_79 = etree.SubElement(
                    credit_transfer_transaction_info_2_27, 'Cdtr')
                creditor_name = etree.SubElement(creditor_2_79, 'Nm')
                creditor_name.text = self._prepare_field(
                    cr, uid, 'Customer Name', 'line.partner_id.name',
                    name_maxsize, line=line, context=context)
                creditor_account_2_80 = etree.SubElement(
                    credit_transfer_transaction_info_2_27, 'CdtrAcct')
                creditor_account_id = etree.SubElement(
                    creditor_account_2_80, 'Id')
                creditor_account_iban = etree.SubElement(
                    creditor_account_id, 'IBAN')
                creditor_account_iban.text = self._validate_iban(
                    cr, uid, self._prepare_field(
                        cr, uid, 'Customer IBAN',
                        'line.bank_id.acc_number', line=line,
                        context=context),
                    context=context)
                remittance_info_2_91 = etree.SubElement(
                    credit_transfer_transaction_info_2_27, 'RmtInf')
                # switch to Structured (Strdr) ?
                # If we do it, beware that the format is not the same
                # between pain 02 and pain 03
                remittance_info_unstructured_2_99 = etree.SubElement(
                    remittance_info_2_91, 'Ustrd')
                remittance_info_unstructured_2_99.text = self._prepare_field(
                    cr, uid, 'Remittance Information', 'line.communication',
                    140, line=line, context=context)

        if pain_flavor in [
                'pain.001.001.03', 'pain.001.001.04', 'pain.001.001.05']:
            nb_of_transactions_1_6.text = nb_of_transactions_2_4.text = \
                str(transactions_count)
            control_sum_1_7.text = control_sum_2_5.text = \
                '%.2f' % amount_control_sum
        else:
            nb_of_transactions_1_6.text = str(transactions_count)
            control_sum_1_7.text = '%.2f' % amount_control_sum

        xml_string = etree.tostring(
            root, pretty_print=True, encoding='UTF-8', xml_declaration=True)
        _logger.debug(
            "Generated SEPA Credit Transfer XML file in format %s below"
            % pain_flavor)
        _logger.debug(xml_string)
        self._validate_xml(cr, uid, xml_string, pain_flavor)

        # CREATE the banking.export.sepa record
        file_id = self.pool.get('banking.export.sepa').create(
            cr, uid, self._prepare_export_sepa(
                cr, uid, sepa_export, total_amount, transactions_count,
                xml_string, context=context),
            context=context)

        self.write(
            cr, uid, ids, {
                'file_id': file_id,
                'state': 'finish',
            }, context=context)

        action = {
            'name': 'SEPA Credit Transfer File',
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
        self.pool.get('banking.export.sepa').unlink(
            cr, uid, sepa_export.file_id.id, context=context)
        return {'type': 'ir.actions.act_window_close'}

    def save_sepa(self, cr, uid, ids, context=None):
        '''
        Save the SEPA PAIN: send the done signal to all payment
        orders in the file. With the default workflow, they will
        transition to 'done', while with the advanced workflow in
        account_banking_payment they will transition to 'sent' waiting
        reconciliation.
        '''
        sepa_export = self.browse(cr, uid, ids[0], context=context)
        self.pool.get('banking.export.sepa').write(
            cr, uid, sepa_export.file_id.id, {'state': 'sent'},
            context=context)
        wf_service = netsvc.LocalService('workflow')
        for order in sepa_export.payment_order_ids:
            wf_service.trg_validate(uid, 'payment.order', order.id, 'done', cr)
        return {'type': 'ir.actions.act_window_close'}
