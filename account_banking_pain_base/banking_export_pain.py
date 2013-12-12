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
from unidecode import unidecode
from lxml import etree
from openerp import tools
import logging

logger = logging.getLogger(__name__)


class banking_export_pain(orm.AbstractModel):
    _name = 'banking.export.pain'

    def _validate_iban(self, cr, uid, iban, context=None):
        '''if IBAN is valid, returns IBAN
        if IBAN is NOT valid, raises an error message'''
        partner_bank_obj = self.pool.get('res.partner.bank')
        if partner_bank_obj.is_iban_valid(cr, uid, iban, context=context):
            return iban.replace(' ', '')
        else:
            raise orm.except_orm(
                _('Error:'), _("This IBAN is not valid : %s") % iban)

    def _prepare_field(
            self, cr, uid, field_name, field_value, eval_ctx, max_size=0,
            convert_to_ascii=False, context=None):
        '''This function is designed to be inherited !'''
        assert isinstance(eval_ctx, dict), 'eval_ctx must contain a dict'
        try:
            value = safe_eval(field_value, eval_ctx)
            # SEPA uses XML ; XML = UTF-8 ; UTF-8 = support for all characters
            # But we are dealing with banks...
            # and many banks don't want non-ASCCI characters !
            # cf section 1.4 "Character set" of the SEPA Credit Transfer
            # Scheme Customer-to-bank guidelines
            if convert_to_ascii:
                value = unidecode(value)
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

    def _validate_xml(self, cr, uid, xml_string, pain_xsd_file):
        xsd_etree_obj = etree.parse(
            tools.file_open(pain_xsd_file))
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
                _('The generated XML file is not valid against the official XML Schema Definition. The generated XML file and the full error have been written in the server logs. Here is the error, which may give you an idea on the cause of the problem : %s')
                % str(e))
        return True

    def generate_group_header_block(
            self, cr, uid, parent_node, sepa_export, gen_args, context=None):
        group_header_1_0 = etree.SubElement(parent_node, 'GrpHdr')
        message_identification_1_1 = etree.SubElement(
            group_header_1_0, 'MsgId')
        message_identification_1_1.text = self._prepare_field(
            cr, uid, 'Message Identification',
            'sepa_export.payment_order_ids[0].reference',
            {'sepa_export': sepa_export}, 35,
            convert_to_ascii=gen_args.get('convert_to_ascii'), context=context)
        creation_date_time_1_2 = etree.SubElement(group_header_1_0, 'CreDtTm')
        creation_date_time_1_2.text = datetime.strftime(
            datetime.today(), '%Y-%m-%dT%H:%M:%S')
        if gen_args.get('pain_flavor') == 'pain.001.001.02':
            # batch_booking is in "Group header" with pain.001.001.02
            # and in "Payment info" in pain.001.001.03/04
            batch_booking = etree.SubElement(group_header_1_0, 'BtchBookg')
            batch_booking.text = str(sepa_export.batch_booking).lower()
        nb_of_transactions_1_6 = etree.SubElement(
            group_header_1_0, 'NbOfTxs')
        control_sum_1_7 = etree.SubElement(group_header_1_0, 'CtrlSum')
        # Grpg removed in pain.001.001.03
        if gen_args.get('pain_flavor') == 'pain.001.001.02':
            grouping = etree.SubElement(group_header_1_0, 'Grpg')
            grouping.text = 'GRPD'
        self.generate_initiating_party_block(
            cr, uid, group_header_1_0, sepa_export, gen_args,
            context=context)
        return group_header_1_0, nb_of_transactions_1_6, control_sum_1_7

    def generate_initiating_party_block(
            self, cr, uid, parent_node, sepa_export, gen_args,
            context=None):
        my_company_name = self._prepare_field(
            cr, uid, 'Company Name',
            'sepa_export.payment_order_ids[0].mode.bank_id.partner_id.name',
            {'sepa_export': sepa_export}, gen_args.get('name_maxsize'),
            convert_to_ascii=gen_args.get('convert_to_ascii'), context=context)
        initiating_party_1_8 = etree.SubElement(parent_node, 'InitgPty')
        initiating_party_name = etree.SubElement(initiating_party_1_8, 'Nm')
        initiating_party_name.text = my_company_name
        initiating_party_identifier = self.pool['res.company'].\
            _get_initiating_party_identifier(
                cr, uid, sepa_export.payment_order_ids[0].company_id.id,
                context=context)
        initiating_party_issuer = \
            sepa_export.payment_order_ids[0].company_id.initiating_party_issuer
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

    def generate_party_bic(
            self, cr, uid, parent_node, party_type, party_type_label, bic,
            eval_ctx, gen_args, context=None):
        '''Generate the piece of the XML file corresponding to BIC
        This code is mutualized between TRF and DD'''
        party_agent = etree.SubElement(parent_node, '%sAgt' % party_type)
        party_agent_institution = etree.SubElement(
            party_agent, 'FinInstnId')
        party_agent_bic = etree.SubElement(
            party_agent_institution, gen_args.get('bic_xml_tag'))
        party_agent_bic.text = self._prepare_field(
            cr, uid, '%s BIC' % party_type_label, bic, eval_ctx,
            convert_to_ascii=gen_args.get('convert_to_ascii'), context=context)
        return True

    def generate_party_block(
            self, cr, uid, parent_node, party_type, order, name, iban, bic,
            eval_ctx, gen_args, context=None):
        '''Generate the piece of the XML file corresponding to Name+IBAN+BIC
        This code is mutualized between TRF and DD'''
        assert order in ('B', 'C'), "Order can be 'B' or 'C'"
        if party_type == 'Cdtr':
            party_type_label = 'Creditor'
        elif party_type == 'Dbtr':
            party_type_label = 'Debtor'
        # At C level, the order is : BIC, Name, IBAN
        # At B level, the order is : Name, IBAN, BIC
        if order == 'C':
            self.generate_party_bic(
                cr, uid, parent_node, party_type, party_type_label, bic,
                eval_ctx, gen_args, context=context)
        party = etree.SubElement(parent_node, party_type)
        party_name = etree.SubElement(party, 'Nm')
        party_name.text = self._prepare_field(
            cr, uid, '%s Name' % party_type_label, name, eval_ctx,
            gen_args.get('name_maxsize'),
            convert_to_ascii=gen_args.get('convert_to_ascii'), context=context)
        party_account = etree.SubElement(
            parent_node, '%sAcct' % party_type)
        party_account_id = etree.SubElement(party_account, 'Id')
        party_account_iban = etree.SubElement(
            party_account_id, 'IBAN')
        piban = self._prepare_field(
            cr, uid, '%s IBAN' % party_type_label, iban, eval_ctx,
            convert_to_ascii=gen_args.get('convert_to_ascii'),
            context=context)
        viban = self._validate_iban(cr, uid, piban, context=context)
        party_account_iban.text = viban
        if order == 'B':
            self.generate_party_bic(
                cr, uid, parent_node, party_type, party_type_label, bic,
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
                    convert_to_ascii=gen_args.get('convert_to_ascii'),
                    context=context)
        else:
            if not line.struct_communication_type:
                raise orm.except_orm(
                    _('Error:'),
                    _("Missing 'Structured Communication Type' on payment line with your reference '%s'.")
                    % (line.name))
            remittance_info_unstructured_2_100 = etree.SubElement(
                remittance_info_2_91, 'Strd')
            creditor_ref_information_2_120 = etree.SubElement(
                remittance_info_unstructured_2_100, 'CdtrRefInf')
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
                    convert_to_ascii=gen_args.get('convert_to_ascii'),
                    context=context)
        return True
