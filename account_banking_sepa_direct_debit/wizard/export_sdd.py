# -*- encoding: utf-8 -*-
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
from openerp.tools.safe_eval import safe_eval
from openerp import tools, netsvc
import base64
from datetime import datetime, timedelta
from lxml import etree
import logging
from unidecode import unidecode

_logger = logging.getLogger(__name__)


class banking_export_sdd_wizard(orm.TransientModel):
    _name = 'banking.export.sdd.wizard'
    _description = 'Export SEPA Direct Debit File'
    _columns = {
        'state': fields.selection([
            ('create', 'Create'),
            ('finish', 'Finish'),
            ], 'State', readonly=True),
        'batch_booking': fields.boolean(
            'Batch Booking',
            help="If true, the bank statement will display only one debit line for all the wire transfers of the SEPA XML file ; if false, the bank statement will display one debit line per wire transfer of the SEPA XML file."),
        'requested_collec_date': fields.date(
            'Requested Collection Date',
            help='This is the date on which the collection should be made by the bank. Please keep in mind that banks only execute on working days.'),
        'charge_bearer': fields.selection([
            ('SHAR', 'Shared'),
            ('CRED', 'Borne by Creditor'),
            ('DEBT', 'Borne by Debtor'),
            ('SLEV', 'Following Service Level'),
            ], 'Charge Bearer', required=True,
            help='Shared : transaction charges on the sender side are to be borne by the debtor, transaction charges on the receiver side are to be borne by the creditor (most transfers use this). Borne by creditor : all transaction charges are to be borne by the creditor. Borne by debtor : all transaction charges are to be borne by the debtor. Following service level : transaction charges are to be applied following the rules agreed in the service level and/or scheme.'),
        'nb_transactions': fields.related(
            'file_id', 'nb_transactions', type='integer',
            string='Number of Transactions', readonly=True),
        'total_amount': fields.related(
            'file_id', 'total_amount', type='float', string='Total Amount',
            readonly=True),
        'file_id': fields.many2one(
            'banking.export.sdd', 'SDD XML File', readonly=True),
        'file': fields.related(
            'file_id', 'file', string="File", type='binary', readonly=True),
        'filename': fields.related(
            'file_id', 'filename', string="Filename", type='char', size=256,
            readonly=True),
        'payment_order_ids': fields.many2many(
            'payment.order', 'wiz_sdd_payorders_rel', 'wizard_id',
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
        return super(banking_export_sdd_wizard, self).create(
            cr, uid, vals, context=context)

    def _prepare_field(
            self, cr, uid, field_name, field_value, eval_ctx, max_size=0,
            context=None):
        '''This function is designed to be inherited !'''
        assert isinstance(eval_ctx, dict), 'eval_ctx must contain a dict'
        try:
            # SEPA uses XML ; XML = UTF-8 ; UTF-8 = support for all characters
            # But we are dealing with banks...
            # and many banks don't want non-ASCCI characters !
            # cf section 1.4 "Character set" of the SEPA Core Direct Debit
            # Customer-to-bank implementation guidelines
            value = unidecode(safe_eval(field_value, eval_ctx))
        except:
            line = eval_ctx.get('line')
            if line:
                raise orm.except_orm(
                    _('Error:'),
                    _("Cannot compute the '%s' of the Payment Line with Invoice Reference '%s'.")
                    % (field_name, self.pool['account.invoice'].name_get(
                        cr, uid, [line.ml_inv_ref.id], context=context)[0][1]))
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
            'requested_collec_date': sepa_export.requested_collec_date,
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
                'account_banking_sepa_direct_debit/data/%s.xsd'
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

    def _get_previous_bank(self, cr, uid, payline, context=None):
        payline_obj = self.pool['payment.line']
        previous_bank = False
        payline_ids = payline_obj.search(
            cr, uid, [
                ('sdd_mandate_id', '=', payline.sdd_mandate_id.id),
                ('bank_id', '!=', payline.bank_id.id),
            ],
            context=context)
        if payline_ids:
            older_lines = payline_obj.browse(
                cr, uid, payline_ids, context=context)
            previous_date = False
            previous_payline_id = False
            for older_line in older_lines:
                older_line_date_sent = older_line.order_id.date_sent
                if (older_line_date_sent
                        and older_line_date_sent > previous_date):
                    previous_date = older_line_date_sent
                    previous_payline_id = older_line.id
            if previous_payline_id:
                previous_payline = payline_obj.browse(
                    cr, uid, previous_payline_id, context=context)
                previous_bank = previous_payline.bank_id
        return previous_bank

    def create_sepa(self, cr, uid, ids, context=None):
        '''
        Creates the SEPA Direct Debit file. That's the important code !
        '''
        sepa_export = self.browse(cr, uid, ids[0], context=context)

        pain_flavor = sepa_export.payment_order_ids[0].mode.type.code
        if pain_flavor == 'pain.008.001.02':
            bic_xml_tag = 'BIC'
            name_maxsize = 70
            root_xml_tag = 'CstmrDrctDbtInitn'
        elif pain_flavor == 'pain.008.001.03':
            bic_xml_tag = 'BICFI'
            name_maxsize = 140
            root_xml_tag = 'CstmrDrctDbtInitn'
        elif pain_flavor == 'pain.008.001.04':
            bic_xml_tag = 'BICFI'
            name_maxsize = 140
            root_xml_tag = 'CstmrDrctDbtInitn'
        else:
            raise orm.except_orm(_('Error:'), _("Payment Type Code '%s' is not supported. The only Payment Type Code supported for SEPA Direct Debit are 'pain.008.001.02', 'pain.008.001.03' and 'pain.008.001.04'.") % pain_flavor)
        if sepa_export.requested_collec_date:
            my_requested_collec_date = sepa_export.requested_collec_date
        else:
            my_requested_collec_date = datetime.strftime(
                datetime.today() + timedelta(days=1), '%Y-%m-%d')

        pain_ns = {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            None: 'urn:iso:std:iso:20022:tech:xsd:%s' % pain_flavor,
            }

        root = etree.Element('Document', nsmap=pain_ns)
        pain_root = etree.SubElement(root, root_xml_tag)

        my_company_name = self._prepare_field(
            cr, uid, 'Company Name',
            'sepa_export.payment_order_ids[0].company_id.partner_id.name',
            {'sepa_export': sepa_export}, name_maxsize, context=context)

        # A. Group header
        group_header_1_0 = etree.SubElement(pain_root, 'GrpHdr')
        message_identification_1_1 = etree.SubElement(
            group_header_1_0, 'MsgId')
        message_identification_1_1.text = self._prepare_field(
            cr, uid, 'Message Identification',
            'sepa_export.payment_order_ids[0].reference',
            {'sepa_export': sepa_export}, 35, context=context)
        creation_date_time_1_2 = etree.SubElement(group_header_1_0, 'CreDtTm')
        creation_date_time_1_2.text = datetime.strftime(
            datetime.today(), '%Y-%m-%dT%H:%M:%S')
        nb_of_transactions_1_6 = etree.SubElement(group_header_1_0, 'NbOfTxs')
        control_sum_1_7 = etree.SubElement(group_header_1_0, 'CtrlSum')
        initiating_party_1_8 = etree.SubElement(group_header_1_0, 'InitgPty')
        initiating_party_name = etree.SubElement(initiating_party_1_8, 'Nm')
        initiating_party_name.text = my_company_name

        transactions_count_1_6 = 0
        total_amount = 0.0
        amount_control_sum_1_7 = 0.0
        lines_per_seq_type = {}
        # key = sequence type ; value = list of lines as objects
        # Iterate on payment orders
        for payment_order in sepa_export.payment_order_ids:
            total_amount = total_amount + payment_order.total
            # Iterate each payment lines
            for line in payment_order.line_ids:
                transactions_count_1_6 += 1
                if not line.sdd_mandate_id:
                    raise orm.except_orm(
                        _('Error:'),
                        _("Missing SEPA Direct Debit mandate on the payment line with partner '%s' and Invoice ref '%s'.")
                        % (line.partner_id.name,
                            line.ml_inv_ref.number))
                if line.sdd_mandate_id.state != 'valid':
                    raise orm.except_orm(
                        _('Error:'),
                        _("The SEPA Direct Debit mandate with reference '%s' for partner '%s' has expired.")
                        % (line.sdd_mandate_id.unique_mandate_reference,
                            line.sdd_mandate_id.partner_id.name))
                if not line.sdd_mandate_id.signature_date:
                    raise orm.except_orm(
                        _('Error:'),
                        _("Missing signature date on SEPA Direct Debit mandate with reference '%s' for partner '%s'.")
                        % (line.sdd_mandate_id.unique_mandate_reference,
                            line.sdd_mandate_id.partner_id.name))
                elif (line.sdd_mandate_id.signature_date >
                        datetime.today().strftime('%Y-%m-%d')):
                    raise orm.except_orm(
                        _('Error:'),
                        _("The signature date on SEPA Direct Debit mandate with reference '%s' for partner '%s' is '%s', which is in the future !")
                        % (line.sdd_mandate_id.unique_mandate_reference,
                            line.sdd_mandate_id.partner_id.name,
                            line.sdd_mandate_id.signature_date))
                if line.sdd_mandate_id.type == 'oneoff':
                    if not line.sdd_mandate_id.last_debit_date:
                        if lines_per_seq_type.get('OOFF'):
                            lines_per_seq_type['OOFF'].append(line)
                        else:
                            lines_per_seq_type['OOFF'] = [line]
                    else:
                        raise orm.except_orm(
                            _('Error:'),
                            _("The mandate with reference '%s' for partner '%s' has type set to 'One-Off' and it has a last debit date set to '%s', so we can't use it.")
                            % (line.sdd_mandate_id.unique_mandate_reference,
                                line.sdd_mandate_id.partner_id.name,
                                line.sdd_mandate_id.last_debit_date))
                elif line.sdd_mandate_id.type == 'recurrent':
                    seq_type_map = {
                        'recurring': 'RCUR',
                        'first': 'FRST',
                        'final': 'FNAL',
                        }
                    seq_type_label = line.sdd_mandate_id.recurrent_sequence_type
                    assert seq_type_label is not False
                    seq_type = seq_type_map[seq_type_label]
                    if lines_per_seq_type.get(seq_type):
                        lines_per_seq_type[seq_type].append(line)
                    else:
                        lines_per_seq_type[seq_type] = [line]

        for sequence_type, lines in lines_per_seq_type.items():
            # B. Payment info
            payment_info_2_0 = etree.SubElement(pain_root, 'PmtInf')
            payment_info_identification_2_1 = etree.SubElement(
                payment_info_2_0, 'PmtInfId')
            payment_info_identification_2_1.text = self._prepare_field(
                cr, uid, 'Payment Information Identification',
                "sequence_type + '-' + sepa_export.payment_order_ids[0].reference",
                {'sepa_export': sepa_export, 'sequence_type': sequence_type},
                35, context=context)
            payment_method_2_2 = etree.SubElement(payment_info_2_0, 'PmtMtd')
            payment_method_2_2.text = 'DD'
            # batch_booking is in "Payment Info" with pain.008.001.02/03
            batch_booking_2_3 = etree.SubElement(payment_info_2_0, 'BtchBookg')
            batch_booking_2_3.text = str(sepa_export.batch_booking).lower()
            # The "SEPA Core Direct Debit Scheme Customer-to-bank
            # Implementation guidelines" v6.0 says that control sum
            # and nb_of_transactions should be present
            # at both "group header" level and "payment info" level
            nb_of_transactions_2_4 = etree.SubElement(
                payment_info_2_0, 'NbOfTxs')
            control_sum_2_5 = etree.SubElement(payment_info_2_0, 'CtrlSum')
            payment_type_info_2_6 = etree.SubElement(
                payment_info_2_0, 'PmtTpInf')
            service_level_2_8 = etree.SubElement(
                payment_type_info_2_6, 'SvcLvl')
            service_level_code_2_9 = etree.SubElement(service_level_2_8, 'Cd')
            service_level_code_2_9.text = 'SEPA'
            local_instrument_2_11 = etree.SubElement(
                payment_type_info_2_6, 'LclInstrm')
            local_instr_code_2_12 = etree.SubElement(
                local_instrument_2_11, 'Cd')
            local_instr_code_2_12.text = 'CORE'
            # 2.14 Sequence Type MANDATORY
            # this message element must indicate ‘FRST
            # 'FRST' = First ; 'OOFF' = One Off ; 'RCUR' : Recurring
            # 'FNAL' = Final
            sequence_type_2_14 = etree.SubElement(
                payment_type_info_2_6, 'SeqTp')
            sequence_type_2_14.text = sequence_type

            requested_collec_date_2_18 = etree.SubElement(
                payment_info_2_0, 'ReqdColltnDt')
            requested_collec_date_2_18.text = my_requested_collec_date
            creditor_2_19 = etree.SubElement(payment_info_2_0, 'Cdtr')
            creditor_name = etree.SubElement(creditor_2_19, 'Nm')
            creditor_name.text = my_company_name
            creditor_account_2_20 = etree.SubElement(
                payment_info_2_0, 'CdtrAcct')
            creditor_account_id = etree.SubElement(creditor_account_2_20, 'Id')
            creditor_account_iban = etree.SubElement(
                creditor_account_id, 'IBAN')
            creditor_account_iban.text = self._validate_iban(
                cr, uid, self._prepare_field(
                    cr, uid, 'Company IBAN',
                    'sepa_export.payment_order_ids[0].mode.bank_id.acc_number',
                    {'sepa_export': sepa_export}, context=context),
                context=context)

            creditor_agent_2_21 = etree.SubElement(payment_info_2_0, 'CdtrAgt')
            creditor_agent_institution = etree.SubElement(
                creditor_agent_2_21, 'FinInstnId')
            creditor_agent_bic = etree.SubElement(
                creditor_agent_institution, bic_xml_tag)
            creditor_agent_bic.text = self._prepare_field(
                cr, uid, 'Company BIC',
                'sepa_export.payment_order_ids[0].mode.bank_id.bank.bic',
                {'sepa_export': sepa_export}, context=context)

            charge_bearer_2_24 = etree.SubElement(payment_info_2_0, 'ChrgBr')
            charge_bearer_2_24.text = sepa_export.charge_bearer

            creditor_scheme_identification_2_27 = etree.SubElement(
                payment_info_2_0, 'CdtrSchmeId')
            csi_id = etree.SubElement(
                creditor_scheme_identification_2_27, 'Id')
            csi_privateid = csi_id = etree.SubElement(csi_id, 'PrvtId')
            csi_other = etree.SubElement(csi_privateid, 'Othr')
            csi_other_id = etree.SubElement(csi_other, 'Id')
            csi_other_id.text = self._prepare_field(
                cr, uid, 'SEPA Creditor Identifier',
                'sepa_export.payment_order_ids[0].company_id.sepa_creditor_identifier',
                {'sepa_export': sepa_export}, context=context)
            csi_scheme_name = etree.SubElement(csi_other, 'SchmeNm')
            csi_scheme_name_proprietary = etree.SubElement(
                csi_scheme_name, 'Prtry')
            csi_scheme_name_proprietary.text = 'SEPA'

            transactions_count_2_4 = 0
            amount_control_sum_2_5 = 0.0
            for line in lines:
                transactions_count_2_4 += 1
                # C. Direct Debit Transaction Info
                dd_transaction_info_2_28 = etree.SubElement(
                    payment_info_2_0, 'DrctDbtTxInf')
                payment_identification_2_29 = etree.SubElement(
                    dd_transaction_info_2_28, 'PmtId')
                end2end_identification_2_31 = etree.SubElement(
                    payment_identification_2_29, 'EndToEndId')
                end2end_identification_2_31.text = self._prepare_field(
                    cr, uid, 'End to End Identification', 'line.name',
                    {'line': line}, 35, context=context)
                currency_name = self._prepare_field(
                    cr, uid, 'Currency Code', 'line.currency.name',
                    {'line': line}, 3, context=context)
                instructed_amount_2_44 = etree.SubElement(
                    dd_transaction_info_2_28, 'InstdAmt', Ccy=currency_name)
                instructed_amount_2_44.text = '%.2f' % line.amount_currency
                amount_control_sum_1_7 += line.amount_currency
                amount_control_sum_2_5 += line.amount_currency
                dd_transaction_2_46 = etree.SubElement(
                    dd_transaction_info_2_28, 'DrctDbtTx')
                mandate_related_info_2_47 = etree.SubElement(
                    dd_transaction_2_46, 'MndtRltdInf')
                mandate_identification_2_48 = etree.SubElement(
                    mandate_related_info_2_47, 'MndtId')
                mandate_identification_2_48.text = self._prepare_field(
                    cr, uid, 'Unique Mandate Reference',
                    'line.sdd_mandate_id.unique_mandate_reference',
                    {'line': line}, 35, context=context)
                mandate_signature_date_2_49 = etree.SubElement(
                    mandate_related_info_2_47, 'DtOfSgntr')
                mandate_signature_date_2_49.text = self._prepare_field(
                    cr, uid, 'Mandate Signature Date',
                    'line.sdd_mandate_id.signature_date',
                    {'line': line}, 10, context=context)
                if (sequence_type == 'FRST'
                        and line.sdd_mandate_id.last_debit_date):
                    previous_bank = self._get_previous_bank(
                        cr, uid, line, context=context)
                    if previous_bank:
                        amendment_indicator_2_50 = etree.SubElement(
                            mandate_related_info_2_47, 'AmdmntInd')
                        amendment_indicator_2_50.text = 'true'
                        amendment_info_details_2_51 = etree.SubElement(
                            mandate_related_info_2_47, 'AmdmntInfDtls')
                        if previous_bank.bank.bic == line.bank_id.bank.bic:
                            ori_debtor_account_2_57 = etree.SubElement(
                                amendment_info_details_2_51, 'OrgnlDbtrAcct')
                            ori_debtor_account_id = etree.SubElement(
                                ori_debtor_account_2_57, 'Id')
                            ori_debtor_account_iban = etree.SubElement(
                                ori_debtor_account_id, 'IBAN')
                            ori_debtor_account_iban.text = self._validate_iban(
                                cr, uid, self._prepare_field(
                                    cr, uid, 'Original Debtor Account',
                                    'previous_bank.acc_number',
                                    {'previous_bank': previous_bank},
                                    context=context),
                                context=context)
                        else:
                            ori_debtor_agent_2_58 = etree.SubElement(
                                amendment_info_details_2_51, 'OrgnlDbtrAgt')
                            ori_debtor_agent_institution = etree.SubElement(
                                ori_debtor_agent_2_58, 'FinInstnId')
                            ori_debtor_agent_bic = etree.SubElement(
                                ori_debtor_agent_institution, bic_xml_tag)
                            ori_debtor_agent_bic.text = self._prepare_field(
                                cr, uid, 'Original Debtor Agent',
                                'previous_bank.bank.bic',
                                {'previous_bank': previous_bank},
                                context=context)
                            ori_debtor_agent_other = etree.SubElement(
                                ori_debtor_agent_institution, 'Othr')
                            ori_debtor_agent_other_id = etree.SubElement(
                                ori_debtor_agent_other, 'Id')
                            ori_debtor_agent_other_id.text = 'SMNDA'
                            # SMNDA = Same Mandate New Debtor Agent

                debtor_agent_2_70 = etree.SubElement(
                    dd_transaction_info_2_28, 'DbtrAgt')
                debtor_agent_institution = etree.SubElement(
                    debtor_agent_2_70, 'FinInstnId')
                debtor_agent_bic = etree.SubElement(
                    debtor_agent_institution, bic_xml_tag)
                debtor_agent_bic.text = self._prepare_field(
                    cr, uid, 'Customer BIC', 'line.bank_id.bank.bic',
                    {'line': line}, context=context)
                debtor_2_72 = etree.SubElement(
                    dd_transaction_info_2_28, 'Dbtr')
                debtor_name = etree.SubElement(debtor_2_72, 'Nm')
                debtor_name.text = self._prepare_field(
                    cr, uid, 'Customer Name', 'line.partner_id.name',
                    {'line': line}, name_maxsize, context=context)
                debtor_account_2_73 = etree.SubElement(
                    dd_transaction_info_2_28, 'DbtrAcct')
                debtor_account_id = etree.SubElement(debtor_account_2_73, 'Id')
                debtor_account_iban = etree.SubElement(
                    debtor_account_id, 'IBAN')
                debtor_account_iban.text = self._validate_iban(
                    cr, uid, self._prepare_field(
                        cr, uid, 'Customer IBAN',
                        'line.bank_id.acc_number', {'line': line},
                        context=context),
                    context=context)
                remittance_info_2_88 = etree.SubElement(
                    dd_transaction_info_2_28, 'RmtInf')
                # switch to Structured (Strdr) ? If we do it, beware that the format is not the same between pain 02 and pain 03
                remittance_info_unstructured_2_89 = etree.SubElement(
                    remittance_info_2_88, 'Ustrd')
                remittance_info_unstructured_2_89.text = self._prepare_field(
                    cr, uid, 'Remittance Information', 'line.communication',
                    {'line': line}, 140, context=context)
            nb_of_transactions_2_4.text = str(transactions_count_2_4)
            control_sum_2_5.text = '%.2f' % amount_control_sum_2_5
        nb_of_transactions_1_6.text = str(transactions_count_1_6)
        control_sum_1_7.text = '%.2f' % amount_control_sum_1_7

        xml_string = etree.tostring(
            root, pretty_print=True, encoding='UTF-8', xml_declaration=True)
        _logger.debug(
            "Generated SDD XML file in format %s below" % pain_flavor)
        _logger.debug(xml_string)
        self._validate_xml(cr, uid, xml_string, pain_flavor)

        # CREATE the banking.export.sepa record
        file_id = self.pool.get('banking.export.sdd').create(
            cr, uid, self._prepare_export_sepa(
                cr, uid, sepa_export, total_amount, transactions_count_1_6,
                xml_string, context=context),
            context=context)

        self.write(
            cr, uid, ids, {
                'file_id': file_id,
                'state': 'finish',
            }, context=context)

        action = {
            'name': 'SEPA Direct Debit File',
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
        Cancel the SEPA Direct Debit file: just drop the file
        '''
        sepa_export = self.browse(cr, uid, ids[0], context=context)
        self.pool.get('banking.export.sdd').unlink(
            cr, uid, sepa_export.file_id.id, context=context)
        return {'type': 'ir.actions.act_window_close'}

    def save_sepa(self, cr, uid, ids, context=None):
        '''
        Save the SEPA Direct Debit file: mark all payments in the file
        as 'sent'. Write 'last debit date' on mandate and set oneoff
        mandate to expired
        '''
        sepa_export = self.browse(cr, uid, ids[0], context=context)
        self.pool.get('banking.export.sdd').write(
            cr, uid, sepa_export.file_id.id, {'state': 'sent'},
            context=context)
        wf_service = netsvc.LocalService('workflow')
        for order in sepa_export.payment_order_ids:
            wf_service.trg_validate(uid, 'payment.order', order.id, 'done', cr)
            mandate_ids = [line.sdd_mandate_id.id for line in order.line_ids]
            self.pool['sdd.mandate'].write(
                cr, uid, mandate_ids,
                {'last_debit_date': datetime.today().strftime('%Y-%m-%d')},
                context=context)
            to_expire_ids = []
            first_mandate_ids = []
            for line in order.line_ids:
                if line.sdd_mandate_id.type == 'oneoff':
                    to_expire_ids.append(line.sdd_mandate_id.id)
                elif line.sdd_mandate_id.type == 'recurrent':
                    seq_type = line.sdd_mandate_id.recurrent_sequence_type
                    if seq_type == 'final':
                        to_expire_ids.append(line.sdd_mandate_id.id)
                    elif seq_type == 'first':
                        first_mandate_ids.append(line.sdd_mandate_id.id)
            self.pool['sdd.mandate'].write(
                cr, uid, to_expire_ids, {'state': 'expired'}, context=context)
            self.pool['sdd.mandate'].write(
                cr, uid, first_mandate_ids,
                {'recurrent_sequence_type': 'recurring'}, context=context)
        return {'type': 'ir.actions.act_window_close'}
