# -*- encoding: utf-8 -*-
##############################################################################
#
#    PAIN Base module for OpenERP
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

from openerp.osv import orm
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval
from datetime import datetime
from lxml import etree
from openerp import tools
import logging
import base64


try:
    from unidecode import unidecode
except ImportError:
    unidecode = None

logger = logging.getLogger(__name__)


class BankingExportPain(orm.AbstractModel):
    _name = 'banking.export.pain'

    def _validate_iban(self, cr, uid, iban, context=None):
        """if IBAN is valid, returns IBAN
        if IBAN is NOT valid, raises an error message"""
        partner_bank_obj = self.pool.get('res.partner.bank')
        if partner_bank_obj.is_iban_valid(cr, uid, iban, context=context):
            return iban.replace(' ', '')
        else:
            raise orm.except_orm(
                _('Error:'), _("This IBAN is not valid : %s") % iban)

    def _prepare_field(self, cr, uid, field_name, field_value, eval_ctx,
                       max_size=0, gen_args=None, context=None):
        """This function is designed to be inherited !"""
        if gen_args is None:
            gen_args = {}
        assert isinstance(eval_ctx, dict), 'eval_ctx must contain a dict'
        try:
            value = safe_eval(field_value, eval_ctx)
            # SEPA uses XML ; XML = UTF-8 ; UTF-8 = support for all characters
            # But we are dealing with banks...
            # and many banks don't want non-ASCCI characters !
            # cf section 1.4 "Character set" of the SEPA Credit Transfer
            # Scheme Customer-to-bank guidelines
            if gen_args.get('convert_to_ascii'):
                value = unidecode(value)
                unallowed_ascii_chars = [
                    '"', '#', '$', '%', '&', '*', ';', '<', '>', '=', '@',
                    '[', ']', '^', '_', '`', '{', '}', '|', '~', '\\', '!']
                for unallowed_ascii_char in unallowed_ascii_chars:
                    value = value.replace(unallowed_ascii_char, '-')
        except:
            line = eval_ctx.get('line')
            if line:
                raise orm.except_orm(
                    _('Error:'),
                    _("Cannot compute the '%s' of the Payment Line with "
                        "reference '%s'.")
                    % (field_name, line.name))
            else:
                raise orm.except_orm(
                    _('Error:'),
                    _("Cannot compute the '%s'.") % field_name)
        if not isinstance(value, (str, unicode)):
            raise orm.except_orm(
                _('Field type error:'),
                _("The type of the field '%s' is %s. It should be a string "
                    "or unicode.")
                % (field_name, type(value)))
        if not value:
            raise orm.except_orm(
                _('Error:'),
                _("The '%s' is empty or 0. It should have a non-null value.")
                % field_name)
        if max_size and len(value) > max_size:
            value = value[0:max_size]
        return value

    def _validate_xml(self, cr, uid, xml_string, gen_args, context=None):
        xsd_etree_obj = etree.parse(
            tools.file_open(gen_args['pain_xsd_file']))
        official_pain_schema = etree.XMLSchema(xsd_etree_obj)

        try:
            root_to_validate = etree.fromstring(xml_string)
            official_pain_schema.assertValid(root_to_validate)
        except Exception, e:
            logger.warning(
                "The XML file is invalid against the XML Schema Definition")
            logger.warning(xml_string)
            logger.warning(e)
            raise orm.except_orm(
                _('Error:'),
                _("The generated XML file is not valid against the official "
                    "XML Schema Definition. The generated XML file and the "
                    "full error have been written in the server logs. Here "
                    "is the error, which may give you an idea on the cause "
                    "of the problem : %s")
                % str(e))
        return True

    def finalize_sepa_file_creation(
            self, cr, uid, ids, xml_root, total_amount, transactions_count,
            gen_args, context=None):
        xml_string = etree.tostring(
            xml_root, pretty_print=True, encoding='UTF-8',
            xml_declaration=True)
        logger.debug(
            "Generated SEPA XML file in format %s below"
            % gen_args['pain_flavor'])
        logger.debug(xml_string)
        self._validate_xml(cr, uid, xml_string, gen_args, context=context)

        order_ref = []
        for order in gen_args['sepa_export'].payment_order_ids:
            if order.reference:
                order_ref.append(order.reference.replace('/', '-'))
        filename = '%s%s.xml' % (gen_args['file_prefix'], '-'.join(order_ref))

        self.write(
            cr, uid, ids, {
                'nb_transactions': transactions_count,
                'total_amount': total_amount,
                'filename': filename,
                'file': base64.encodestring(xml_string),
                'state': 'finish',
            }, context=context)

        action = {
            'name': 'SEPA File',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': self._name,
            'res_id': ids[0],
            'target': 'new',
        }
        return action

    def generate_group_header_block(
            self, cr, uid, parent_node, gen_args, context=None):
        group_header_1_0 = etree.SubElement(parent_node, 'GrpHdr')
        message_identification_1_1 = etree.SubElement(
            group_header_1_0, 'MsgId')
        message_identification_1_1.text = self._prepare_field(
            cr, uid, 'Message Identification',
            'sepa_export.payment_order_ids[0].reference',
            {'sepa_export': gen_args['sepa_export']}, 35,
            gen_args=gen_args, context=context)
        creation_date_time_1_2 = etree.SubElement(group_header_1_0, 'CreDtTm')
        creation_date_time_1_2.text = datetime.strftime(
            datetime.today(), '%Y-%m-%dT%H:%M:%S')
        if gen_args.get('pain_flavor') == 'pain.001.001.02':
            # batch_booking is in "Group header" with pain.001.001.02
            # and in "Payment info" in pain.001.001.03/04
            batch_booking = etree.SubElement(group_header_1_0, 'BtchBookg')
            batch_booking.text = \
                str(gen_args['sepa_export'].batch_booking).lower()
        nb_of_transactions_1_6 = etree.SubElement(
            group_header_1_0, 'NbOfTxs')
        control_sum_1_7 = etree.SubElement(group_header_1_0, 'CtrlSum')
        # Grpg removed in pain.001.001.03
        if gen_args.get('pain_flavor') == 'pain.001.001.02':
            grouping = etree.SubElement(group_header_1_0, 'Grpg')
            grouping.text = 'GRPD'
        self.generate_initiating_party_block(
            cr, uid, group_header_1_0, gen_args,
            context=context)
        return group_header_1_0, nb_of_transactions_1_6, control_sum_1_7

    def generate_start_payment_info_block(
            self, cr, uid, parent_node, payment_info_ident,
            priority, local_instrument, sequence_type, requested_date,
            eval_ctx, gen_args, context=None):
        payment_info_2_0 = etree.SubElement(parent_node, 'PmtInf')
        payment_info_identification_2_1 = etree.SubElement(
            payment_info_2_0, 'PmtInfId')
        payment_info_identification_2_1.text = self._prepare_field(
            cr, uid, 'Payment Information Identification',
            payment_info_ident, eval_ctx, 35,
            gen_args=gen_args, context=context)
        payment_method_2_2 = etree.SubElement(payment_info_2_0, 'PmtMtd')
        payment_method_2_2.text = gen_args['payment_method']
        nb_of_transactions_2_4 = False
        control_sum_2_5 = False
        if gen_args.get('pain_flavor') != 'pain.001.001.02':
            batch_booking_2_3 = etree.SubElement(payment_info_2_0, 'BtchBookg')
            batch_booking_2_3.text = \
                str(gen_args['sepa_export'].batch_booking).lower()
        # The "SEPA Customer-to-bank
        # Implementation guidelines" for SCT and SDD says that control sum
        # and nb_of_transactions should be present
        # at both "group header" level and "payment info" level
            nb_of_transactions_2_4 = etree.SubElement(
                payment_info_2_0, 'NbOfTxs')
            control_sum_2_5 = etree.SubElement(payment_info_2_0, 'CtrlSum')
        payment_type_info_2_6 = etree.SubElement(
            payment_info_2_0, 'PmtTpInf')
        if priority and gen_args['payment_method'] != 'DD':
            instruction_priority_2_7 = etree.SubElement(
                payment_type_info_2_6, 'InstrPrty')
            instruction_priority_2_7.text = priority
        service_level_2_8 = etree.SubElement(
            payment_type_info_2_6, 'SvcLvl')
        service_level_code_2_9 = etree.SubElement(service_level_2_8, 'Cd')
        service_level_code_2_9.text = 'SEPA'
        if local_instrument:
            local_instrument_2_11 = etree.SubElement(
                payment_type_info_2_6, 'LclInstrm')
            local_instr_code_2_12 = etree.SubElement(
                local_instrument_2_11, 'Cd')
            local_instr_code_2_12.text = local_instrument
        if sequence_type:
            sequence_type_2_14 = etree.SubElement(
                payment_type_info_2_6, 'SeqTp')
            sequence_type_2_14.text = sequence_type

        if gen_args['payment_method'] == 'DD':
            request_date_tag = 'ReqdColltnDt'
        else:
            request_date_tag = 'ReqdExctnDt'
        requested_date_2_17 = etree.SubElement(
            payment_info_2_0, request_date_tag)
        requested_date_2_17.text = requested_date
        return payment_info_2_0, nb_of_transactions_2_4, control_sum_2_5

    def generate_initiating_party_block(
            self, cr, uid, parent_node, gen_args, context=None):
        my_company_name = self._prepare_field(
            cr, uid, 'Company Name',
            'sepa_export.payment_order_ids[0].mode.bank_id.partner_id.name',
            {'sepa_export': gen_args['sepa_export']},
            gen_args.get('name_maxsize'), gen_args=gen_args, context=context)
        initiating_party_1_8 = etree.SubElement(parent_node, 'InitgPty')
        initiating_party_name = etree.SubElement(initiating_party_1_8, 'Nm')
        initiating_party_name.text = my_company_name
        initiating_party_identifier = self.pool['res.company'].\
            _get_initiating_party_identifier(
                cr, uid,
                gen_args['sepa_export'].payment_order_ids[0].company_id.id,
                context=context)
        initiating_party_issuer = gen_args['sepa_export'].\
            payment_order_ids[0].company_id.initiating_party_issuer
        if initiating_party_identifier and initiating_party_issuer:
            iniparty_id = etree.SubElement(initiating_party_1_8, 'Id')
            iniparty_org_id = etree.SubElement(iniparty_id, 'OrgId')
            iniparty_org_other = etree.SubElement(iniparty_org_id, 'Othr')
            iniparty_org_other_id = etree.SubElement(iniparty_org_other, 'Id')
            iniparty_org_other_id.text = initiating_party_identifier
            iniparty_org_other_issuer = etree.SubElement(
                iniparty_org_other, 'Issr')
            iniparty_org_other_issuer.text = initiating_party_issuer
        return True

    def generate_party_agent(
            self, cr, uid, parent_node, party_type, party_type_label,
            order, party_name, iban, bic, eval_ctx, gen_args, context=None):
        """Generate the piece of the XML file corresponding to BIC
        This code is mutualized between TRF and DD"""
        assert order in ('B', 'C'), "Order can be 'B' or 'C'"
        try:
            bic = self._prepare_field(
                cr, uid, '%s BIC' % party_type_label, bic, eval_ctx,
                gen_args=gen_args, context=context)
            party_agent = etree.SubElement(parent_node, '%sAgt' % party_type)
            party_agent_institution = etree.SubElement(
                party_agent, 'FinInstnId')
            party_agent_bic = etree.SubElement(
                party_agent_institution, gen_args.get('bic_xml_tag'))
            party_agent_bic.text = bic
        except orm.except_orm:
            if order == 'C':
                if iban[0:2] != gen_args['initiating_party_country_code']:
                    raise orm.except_orm(
                        _('Error:'),
                        _("The bank account with IBAN '%s' of partner '%s' "
                            "must have an associated BIC because it is a "
                            "cross-border SEPA operation.")
                        % (iban, party_name))
            if order == 'B' or (
                    order == 'C' and gen_args['payment_method'] == 'DD'):
                party_agent = etree.SubElement(
                    parent_node, '%sAgt' % party_type)
                party_agent_institution = etree.SubElement(
                    party_agent, 'FinInstnId')
                party_agent_other = etree.SubElement(
                    party_agent_institution, 'Othr')
                party_agent_other_identification = etree.SubElement(
                    party_agent_other, 'Id')
                party_agent_other_identification.text = 'NOTPROVIDED'
            # for Credit Transfers, in the 'C' block, if BIC is not provided,
            # we should not put the 'Creditor Agent' block at all,
            # as per the guidelines of the EPC
        return True

    def generate_party_block(
            self, cr, uid, parent_node, party_type, order, name, iban, bic,
            eval_ctx, gen_args, context=None):
        """Generate the piece of the XML file corresponding to Name+IBAN+BIC
        This code is mutualized between TRF and DD"""
        assert order in ('B', 'C'), "Order can be 'B' or 'C'"
        if party_type == 'Cdtr':
            party_type_label = 'Creditor'
        elif party_type == 'Dbtr':
            party_type_label = 'Debtor'
        party_name = self._prepare_field(
            cr, uid, '%s Name' % party_type_label, name, eval_ctx,
            gen_args.get('name_maxsize'),
            gen_args=gen_args, context=context)
        piban = self._prepare_field(
            cr, uid, '%s IBAN' % party_type_label, iban, eval_ctx,
            gen_args=gen_args,
            context=context)
        viban = self._validate_iban(cr, uid, piban, context=context)
        # At C level, the order is : BIC, Name, IBAN
        # At B level, the order is : Name, IBAN, BIC
        if order == 'B':
            gen_args['initiating_party_country_code'] = viban[0:2]
        elif order == 'C':
            self.generate_party_agent(
                cr, uid, parent_node, party_type, party_type_label,
                order, party_name, viban, bic,
                eval_ctx, gen_args, context=context)
        party = etree.SubElement(parent_node, party_type)
        party_nm = etree.SubElement(party, 'Nm')
        party_nm.text = party_name
        party_account = etree.SubElement(
            parent_node, '%sAcct' % party_type)
        party_account_id = etree.SubElement(party_account, 'Id')
        party_account_iban = etree.SubElement(
            party_account_id, 'IBAN')
        party_account_iban.text = viban
        if order == 'B':
            self.generate_party_agent(
                cr, uid, parent_node, party_type, party_type_label,
                order, party_name, viban, bic,
                eval_ctx, gen_args, context=context)
        return True

    def generate_remittance_info_block(
            self, cr, uid, parent_node, line, gen_args, context=None):

        remittance_info_2_91 = etree.SubElement(
            parent_node, 'RmtInf')
        if line.state == 'normal':
            remittance_info_unstructured_2_99 = etree.SubElement(
                remittance_info_2_91, 'Ustrd')
            remittance_info_unstructured_2_99.text = \
                self._prepare_field(
                    cr, uid, 'Remittance Unstructured Information',
                    'line.communication', {'line': line}, 140,
                    gen_args=gen_args,
                    context=context)
        else:
            if not line.struct_communication_type:
                raise orm.except_orm(
                    _('Error:'),
                    _("Missing 'Structured Communication Type' on payment "
                        "line with reference '%s'.")
                    % line.name)
            remittance_info_structured_2_100 = etree.SubElement(
                remittance_info_2_91, 'Strd')
            creditor_ref_information_2_120 = etree.SubElement(
                remittance_info_structured_2_100, 'CdtrRefInf')
            if gen_args.get('pain_flavor') == 'pain.001.001.02':
                creditor_ref_info_type_2_121 = etree.SubElement(
                    creditor_ref_information_2_120, 'CdtrRefTp')
                creditor_ref_info_type_code_2_123 = etree.SubElement(
                    creditor_ref_info_type_2_121, 'Cd')
                creditor_ref_info_type_issuer_2_125 = etree.SubElement(
                    creditor_ref_info_type_2_121, 'Issr')
                creditor_reference_2_126 = etree.SubElement(
                    creditor_ref_information_2_120, 'CdtrRef')
            else:
                creditor_ref_info_type_2_121 = etree.SubElement(
                    creditor_ref_information_2_120, 'Tp')
                creditor_ref_info_type_or_2_122 = etree.SubElement(
                    creditor_ref_info_type_2_121, 'CdOrPrtry')
                creditor_ref_info_type_code_2_123 = etree.SubElement(
                    creditor_ref_info_type_or_2_122, 'Cd')
                creditor_ref_info_type_issuer_2_125 = etree.SubElement(
                    creditor_ref_info_type_2_121, 'Issr')
                creditor_reference_2_126 = etree.SubElement(
                    creditor_ref_information_2_120, 'Ref')

            creditor_ref_info_type_code_2_123.text = 'SCOR'
            creditor_ref_info_type_issuer_2_125.text = \
                line.struct_communication_type
            creditor_reference_2_126.text = \
                self._prepare_field(
                    cr, uid, 'Creditor Structured Reference',
                    'line.communication', {'line': line}, 35,
                    gen_args=gen_args,
                    context=context)
        return True

    def generate_creditor_scheme_identification(
            self, cr, uid, parent_node, identification, identification_label,
            eval_ctx, scheme_name_proprietary, gen_args, context=None):
        csi_id = etree.SubElement(parent_node, 'Id')
        csi_privateid = etree.SubElement(csi_id, 'PrvtId')
        csi_other = etree.SubElement(csi_privateid, 'Othr')
        csi_other_id = etree.SubElement(csi_other, 'Id')
        csi_other_id.text = self._prepare_field(
            cr, uid, identification_label, identification, eval_ctx,
            gen_args=gen_args, context=context)
        csi_scheme_name = etree.SubElement(csi_other, 'SchmeNm')
        csi_scheme_name_proprietary = etree.SubElement(
            csi_scheme_name, 'Prtry')
        csi_scheme_name_proprietary.text = scheme_name_proprietary
        return True
