# -*- coding: utf-8 -*-
# © 2013-2016 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 Antiun Ingenieria S.L. - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from datetime import datetime
from lxml import etree
import logging


try:
    from unidecode import unidecode
except ImportError:
    unidecode = None

logger = logging.getLogger(__name__)


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    sepa = fields.Boolean(
        compute='compute_sepa', readonly=True, string="SEPA Payment")
    charge_bearer = fields.Selection([
        ('SLEV', 'Following Service Level'),
        ('SHAR', 'Shared'),
        ('CRED', 'Borne by Creditor'),
        ('DEBT', 'Borne by Debtor')], string='Charge Bearer',
        default='SLEV', readonly=True,
        states={'draft': [('readonly', False)], 'open': [('readonly', False)]},
        track_visibility='onchange',
        help="Following service level : transaction charges are to be "
        "applied following the rules agreed in the service level "
        "and/or scheme (SEPA Core messages must use this). Shared : "
        "transaction charges on the debtor side are to be borne by "
        "the debtor, transaction charges on the creditor side are to "
        "be borne by the creditor. Borne by creditor : all "
        "transaction charges are to be borne by the creditor. Borne "
        "by debtor : all transaction charges are to be borne by the "
        "debtor.")
    batch_booking = fields.Boolean(
        string='Batch Booking', readonly=True,
        states={'draft': [('readonly', False)], 'open': [('readonly', False)]},
        track_visibility='onchange',
        help="If true, the bank statement will display only one debit "
        "line for all the wire transfers of the SEPA XML file ; if "
        "false, the bank statement will display one debit line per wire "
        "transfer of the SEPA XML file.")

    @api.multi
    @api.depends(
        'company_partner_bank_id.acc_type',
        'payment_line_ids.currency_id',
        'payment_line_ids.partner_bank_id.acc_type')
    def compute_sepa(self):
        eur = self.env.ref('base.EUR')
        for order in self:
            sepa = True
            if order.company_partner_bank_id.acc_type != 'iban':
                sepa = False
            for pline in order.payment_line_ids:
                if pline.currency_id != eur:
                    sepa = False
                    break
                if pline.partner_bank_id.acc_type != 'iban':
                    sepa = False
                    break
            sepa = order.compute_sepa_final_hook(sepa)
            self.sepa = sepa

    @api.multi
    def compute_sepa_final_hook(self, sepa):
        self.ensure_one()
        return sepa

    @api.model
    def _prepare_field(self, field_name, field_value, eval_ctx,
                       max_size=0, gen_args=None):
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
                if isinstance(value, unicode):
                    value = unidecode(value)
                unallowed_ascii_chars = [
                    '"', '#', '$', '%', '&', '*', ';', '<', '>', '=', '@',
                    '[', ']', '^', '_', '`', '{', '}', '|', '~', '\\', '!']
                for unallowed_ascii_char in unallowed_ascii_chars:
                    value = value.replace(unallowed_ascii_char, '-')
        except:
            line = eval_ctx.get('line')
            if line:
                raise UserError(
                    _("Cannot compute the '%s' of the Payment Line with "
                        "reference '%s'.")
                    % (field_name, line.name))
            else:
                raise UserError(
                    _("Cannot compute the '%s'.") % field_name)
        if not isinstance(value, (str, unicode)):
            raise UserError(
                _("The type of the field '%s' is %s. It should be a string "
                    "or unicode.")
                % (field_name, type(value)))
        if not value:
            raise UserError(
                _("The '%s' is empty or 0. It should have a non-null value.")
                % field_name)
        if max_size and len(value) > max_size:
            value = value[0:max_size]
        return value

    @api.model
    def _validate_xml(self, xml_string, gen_args):
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
            raise UserError(
                _("The generated XML file is not valid against the official "
                    "XML Schema Definition. The generated XML file and the "
                    "full error have been written in the server logs. Here "
                    "is the error, which may give you an idea on the cause "
                    "of the problem : %s")
                % unicode(e))
        return True

    @api.multi
    def finalize_sepa_file_creation(self, xml_root, gen_args):
        xml_string = etree.tostring(
            xml_root, pretty_print=True, encoding='UTF-8',
            xml_declaration=True)
        logger.debug(
            "Generated SEPA XML file in format %s below"
            % gen_args['pain_flavor'])
        logger.debug(xml_string)
        self._validate_xml(xml_string, gen_args)

        filename = '%s%s.xml' % (gen_args['file_prefix'], self.name)
        return (xml_string, filename)

    @api.multi
    def generate_pain_nsmap(self):
        self.ensure_one()
        pain_flavor = self.payment_mode_id.payment_method_id.pain_version
        nsmap = {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            None: 'urn:iso:std:iso:20022:tech:xsd:%s' % pain_flavor,
        }
        return nsmap

    @api.multi
    def generate_pain_attrib(self):
        self.ensure_one()
        return {}

    @api.model
    def generate_group_header_block(self, parent_node, gen_args):
        group_header = etree.SubElement(parent_node, 'GrpHdr')
        message_identification = etree.SubElement(
            group_header, 'MsgId')
        message_identification.text = self._prepare_field(
            'Message Identification',
            'self.name',
            {'self': self}, 35, gen_args=gen_args)
        creation_date_time = etree.SubElement(group_header, 'CreDtTm')
        creation_date_time.text = datetime.strftime(
            datetime.today(), '%Y-%m-%dT%H:%M:%S')
        if gen_args.get('pain_flavor') == 'pain.001.001.02':
            # batch_booking is in "Group header" with pain.001.001.02
            # and in "Payment info" in pain.001.001.03/04
            batch_booking = etree.SubElement(group_header, 'BtchBookg')
            batch_booking.text = unicode(self.batch_booking).lower()
        nb_of_transactions = etree.SubElement(
            group_header, 'NbOfTxs')
        control_sum = etree.SubElement(group_header, 'CtrlSum')
        # Grpg removed in pain.001.001.03
        if gen_args.get('pain_flavor') == 'pain.001.001.02':
            grouping = etree.SubElement(group_header, 'Grpg')
            grouping.text = 'GRPD'
        self.generate_initiating_party_block(group_header, gen_args)
        return group_header, nb_of_transactions, control_sum

    @api.model
    def generate_start_payment_info_block(
            self, parent_node, payment_info_ident,
            priority, local_instrument, category_purpose, sequence_type,
            requested_date, eval_ctx, gen_args):
        payment_info = etree.SubElement(parent_node, 'PmtInf')
        payment_info_identification = etree.SubElement(
            payment_info, 'PmtInfId')
        payment_info_identification.text = self._prepare_field(
            'Payment Information Identification',
            payment_info_ident, eval_ctx, 35, gen_args=gen_args)
        payment_method = etree.SubElement(payment_info, 'PmtMtd')
        payment_method.text = gen_args['payment_method']
        nb_of_transactions = False
        control_sum = False
        if gen_args.get('pain_flavor') != 'pain.001.001.02':
            batch_booking = etree.SubElement(payment_info, 'BtchBookg')
            batch_booking.text = unicode(self.batch_booking).lower()
        # The "SEPA Customer-to-bank
        # Implementation guidelines" for SCT and SDD says that control sum
        # and nb_of_transactions should be present
        # at both "group header" level and "payment info" level
            nb_of_transactions = etree.SubElement(
                payment_info, 'NbOfTxs')
            control_sum = etree.SubElement(payment_info, 'CtrlSum')
        payment_type_info = etree.SubElement(
            payment_info, 'PmtTpInf')
        if priority and gen_args['payment_method'] != 'DD':
            instruction_priority = etree.SubElement(
                payment_type_info, 'InstrPrty')
            instruction_priority.text = priority
        if self.sepa:
            service_level = etree.SubElement(payment_type_info, 'SvcLvl')
            service_level_code = etree.SubElement(service_level, 'Cd')
            service_level_code.text = 'SEPA'
        if local_instrument:
            local_instrument_root = etree.SubElement(
                payment_type_info, 'LclInstrm')
            if gen_args.get('local_instrument_type') == 'proprietary':
                local_instr_value = etree.SubElement(
                    local_instrument_root, 'Prtry')
            else:
                local_instr_value = etree.SubElement(
                    local_instrument_root, 'Cd')
            local_instr_value.text = local_instrument
        if sequence_type:
            sequence_type_node = etree.SubElement(
                payment_type_info, 'SeqTp')
            sequence_type_node.text = sequence_type
        if category_purpose:
            category_purpose_node = etree.SubElement(
                payment_type_info, 'CtgyPurp')
            category_purpose_code = etree.SubElement(
                category_purpose_node, 'Cd')
            category_purpose_code.text = category_purpose
        if gen_args['payment_method'] == 'DD':
            request_date_tag = 'ReqdColltnDt'
        else:
            request_date_tag = 'ReqdExctnDt'
        requested_date_node = etree.SubElement(
            payment_info, request_date_tag)
        requested_date_node.text = requested_date
        return payment_info, nb_of_transactions, control_sum

    @api.model
    def _must_have_initiating_party(self, gen_args):
        '''This method is designed to be inherited in localization modules for
        countries in which the initiating party is required'''
        return False

    @api.model
    def generate_initiating_party_block(self, parent_node, gen_args):
        my_company_name = self._prepare_field(
            'Company Name',
            'self.company_partner_bank_id.partner_id.name',
            {'self': self}, gen_args.get('name_maxsize'), gen_args=gen_args)
        initiating_party = etree.SubElement(parent_node, 'InitgPty')
        initiating_party_name = etree.SubElement(initiating_party, 'Nm')
        initiating_party_name.text = my_company_name
        initiating_party_identifier = (
            self.payment_mode_id.initiating_party_identifier or
            self.payment_mode_id.company_id.initiating_party_identifier)
        initiating_party_issuer = (
            self.payment_mode_id.initiating_party_issuer or
            self.payment_mode_id.company_id.initiating_party_issuer)
        initiating_party_scheme = (
            self.payment_mode_id.initiating_party_scheme or
            self.payment_mode_id.company_id.initiating_party_scheme)
        # in pain.008.001.02.ch.01.xsd files they use
        # initiating_party_identifier but not initiating_party_issuer
        if initiating_party_identifier:
            iniparty_id = etree.SubElement(initiating_party, 'Id')
            iniparty_org_id = etree.SubElement(iniparty_id, 'OrgId')
            iniparty_org_other = etree.SubElement(iniparty_org_id, 'Othr')
            iniparty_org_other_id = etree.SubElement(iniparty_org_other, 'Id')
            iniparty_org_other_id.text = initiating_party_identifier
            if initiating_party_scheme:
                iniparty_org_other_scheme = etree.SubElement(
                    iniparty_org_other, 'SchmeNm')
                iniparty_org_other_scheme_name = etree.SubElement(
                    iniparty_org_other_scheme, 'Prtry')
                iniparty_org_other_scheme_name.text = initiating_party_scheme
            if initiating_party_issuer:
                iniparty_org_other_issuer = etree.SubElement(
                    iniparty_org_other, 'Issr')
                iniparty_org_other_issuer.text = initiating_party_issuer
        elif self._must_have_initiating_party(gen_args):
            raise UserError(
                _("Missing 'Initiating Party Issuer' and/or "
                    "'Initiating Party Identifier' for the company '%s'. "
                    "Both fields must have a value.")
                % self.company_id.name)
        return True

    @api.model
    def generate_fininst_postal_address(self, parent_node, bank):
        if not (bank.country or bank.city):
            return
        postal_address = etree.SubElement(parent_node, 'PstlAdr')
        if bank.city:
            etree.SubElement(postal_address, 'TwnNm').text = bank.city
        if bank.country:
            etree.SubElement(postal_address, 'Ctry').text = bank.country.code

    @api.model
    def generate_party_agent(
            self, parent_node, party_type, order, partner_bank, gen_args,
            bank_line=None):
        """Generate the piece of the XML file corresponding to BIC
        This code is mutualized between TRF and DD
        Starting from Feb 1st 2016, we should be able to do
        cross-border SEPA transfers without BIC, cf
        http://www.europeanpaymentscouncil.eu/index.cfm/
        sepa-credit-transfer/iban-and-bic/
        In some localization (l10n_ch_sepa for example), they need the
        bank_line argument"""
        assert order in ('B', 'C'), "Order can be 'B' or 'C'"
        if partner_bank.bank_bic:
            party_agent = etree.SubElement(parent_node, '%sAgt' % party_type)
            party_agent_institution = etree.SubElement(
                party_agent, 'FinInstnId')
            party_agent_bic = etree.SubElement(
                party_agent_institution, gen_args.get('bic_xml_tag'))
            party_agent_bic.text = partner_bank.bank_bic
            self.generate_fininst_postal_address(
                party_agent_institution, partner_bank.bank_id)
        else:
            if order == 'B' or (
                    order == 'C' and gen_args['payment_method'] == 'DD'):
                party_agent = etree.SubElement(
                    parent_node, '%sAgt' % party_type)
                party_agent_institution = etree.SubElement(
                    party_agent, 'FinInstnId')
                self.generate_fininst_postal_address(
                    party_agent_institution, partner_bank.bank_id)
                party_agent_other = etree.SubElement(
                    party_agent_institution, 'Othr')
                party_agent_other_identification = etree.SubElement(
                    party_agent_other, 'Id')
                party_agent_other_identification.text = 'NOTPROVIDED'
            # for Credit Transfers, in the 'C' block, if BIC is not provided,
            # we should not put the 'Creditor Agent' block at all,
            # as per the guidelines of the EPC
        return True

    @api.model
    def generate_party_id(
            self, parent_node, party_type, partner):
        """Generate an Id element for partner inside the parent node.
        party_type can currently be Cdtr or Dbtr. Notably, the initiating
        party orgid is generated with another mechanism and configured
        at the company or payment mode level.
        """
        return

    @api.model
    def generate_party_acc_number(
            self, parent_node, party_type, order, partner_bank, gen_args,
            bank_line=None):
        party_account = etree.SubElement(
            parent_node, '%sAcct' % party_type)
        party_account_id = etree.SubElement(party_account, 'Id')
        if partner_bank.acc_type == 'iban':
            party_account_iban = etree.SubElement(
                party_account_id, 'IBAN')
            party_account_iban.text = partner_bank.sanitized_acc_number
        else:
            party_account_other = etree.SubElement(
                party_account_id, 'Othr')
            party_account_other_id = etree.SubElement(
                party_account_other, 'Id')
            party_account_other_id.text = partner_bank.sanitized_acc_number
        return True

    @api.model
    def generate_party_block(
            self, parent_node, party_type, order, partner_bank, gen_args,
            bank_line=None):
        """Generate the piece of the XML file corresponding to Name+IBAN+BIC
        This code is mutualized between TRF and DD
        In some localization (l10n_ch_sepa for example), they need the
        bank_line argument"""
        assert order in ('B', 'C'), "Order can be 'B' or 'C'"
        if party_type == 'Cdtr':
            party_type_label = 'Creditor'
        elif party_type == 'Dbtr':
            party_type_label = 'Debtor'
        name = 'partner_bank.partner_id.name'
        eval_ctx = {'partner_bank': partner_bank}
        party_name = self._prepare_field(
            '%s Name' % party_type_label, name, eval_ctx,
            gen_args.get('name_maxsize'), gen_args=gen_args)
        # At C level, the order is : BIC, Name, IBAN
        # At B level, the order is : Name, IBAN, BIC
        if order == 'C':
            self.generate_party_agent(
                parent_node, party_type, order, partner_bank, gen_args,
                bank_line=bank_line)
        party = etree.SubElement(parent_node, party_type)
        party_nm = etree.SubElement(party, 'Nm')
        party_nm.text = party_name
        partner = partner_bank.partner_id
        if partner.country_id:
            postal_address = etree.SubElement(party, 'PstlAdr')
            if gen_args.get('pain_flavor').startswith(
                    'pain.001.001.') or gen_args.get('pain_flavor').startswith(
                    'pain.008.001.'):
                if partner.zip:
                    pstcd = etree.SubElement(postal_address, 'PstCd')
                    pstcd.text = self._prepare_field(
                        'Postal Code', 'partner.zip',
                        {'partner': partner}, 16, gen_args=gen_args)
                if partner.city:
                    twnnm = etree.SubElement(postal_address, 'TwnNm')
                    twnnm.text = self._prepare_field(
                        'Town Name', 'partner.city',
                        {'partner': partner}, 35, gen_args=gen_args)
            country = etree.SubElement(postal_address, 'Ctry')
            country.text = self._prepare_field(
                'Country', 'partner.country_id.code',
                {'partner': partner}, 2, gen_args=gen_args)
            if partner.street:
                adrline1 = etree.SubElement(postal_address, 'AdrLine')
                adrline1.text = self._prepare_field(
                    'Adress Line1', 'partner.street',
                    {'partner': partner}, 70, gen_args=gen_args)

        self.generate_party_id(party, party_type, partner)

        self.generate_party_acc_number(
            parent_node, party_type, order, partner_bank, gen_args,
            bank_line=bank_line)

        if order == 'B':
            self.generate_party_agent(
                parent_node, party_type, order, partner_bank, gen_args,
                bank_line=bank_line)
        return True

    @api.model
    def generate_remittance_info_block(self, parent_node, line, gen_args):
        remittance_info = etree.SubElement(
            parent_node, 'RmtInf')
        if line.communication_type == 'normal':
            remittance_info_unstructured = etree.SubElement(
                remittance_info, 'Ustrd')
            remittance_info_unstructured.text = \
                self._prepare_field(
                    'Remittance Unstructured Information',
                    'line.communication', {'line': line}, 140,
                    gen_args=gen_args)
        else:
            remittance_info_structured = etree.SubElement(
                remittance_info, 'Strd')
            creditor_ref_information = etree.SubElement(
                remittance_info_structured, 'CdtrRefInf')
            if gen_args.get('pain_flavor') == 'pain.001.001.02':
                creditor_ref_info_type = etree.SubElement(
                    creditor_ref_information, 'CdtrRefTp')
                creditor_ref_info_type_code = etree.SubElement(
                    creditor_ref_info_type, 'Cd')
                creditor_ref_info_type_code.text = 'SCOR'
                # SCOR means "Structured Communication Reference"
                creditor_ref_info_type_issuer = etree.SubElement(
                    creditor_ref_info_type, 'Issr')
                creditor_ref_info_type_issuer.text = \
                    line.communication_type
                creditor_reference = etree.SubElement(
                    creditor_ref_information, 'CdtrRef')
            else:
                if gen_args.get('structured_remittance_issuer', True):
                    creditor_ref_info_type = etree.SubElement(
                        creditor_ref_information, 'Tp')
                    creditor_ref_info_type_or = etree.SubElement(
                        creditor_ref_info_type, 'CdOrPrtry')
                    creditor_ref_info_type_code = etree.SubElement(
                        creditor_ref_info_type_or, 'Cd')
                    creditor_ref_info_type_code.text = 'SCOR'
                    creditor_ref_info_type_issuer = etree.SubElement(
                        creditor_ref_info_type, 'Issr')
                    creditor_ref_info_type_issuer.text = \
                        line.communication_type

                creditor_reference = etree.SubElement(
                    creditor_ref_information, 'Ref')

            creditor_reference.text = \
                self._prepare_field(
                    'Creditor Structured Reference',
                    'line.communication', {'line': line}, 35,
                    gen_args=gen_args)
        return True

    @api.model
    def generate_creditor_scheme_identification(
            self, parent_node, identification, identification_label,
            eval_ctx, scheme_name_proprietary, gen_args):
        csi_id = etree.SubElement(parent_node, 'Id')
        csi_privateid = etree.SubElement(csi_id, 'PrvtId')
        csi_other = etree.SubElement(csi_privateid, 'Othr')
        csi_other_id = etree.SubElement(csi_other, 'Id')
        csi_other_id.text = self._prepare_field(
            identification_label, identification, eval_ctx, gen_args=gen_args)
        csi_scheme_name = etree.SubElement(csi_other, 'SchmeNm')
        csi_scheme_name_proprietary = etree.SubElement(
            csi_scheme_name, 'Prtry')
        csi_scheme_name_proprietary.text = scheme_name_proprietary
        return True
