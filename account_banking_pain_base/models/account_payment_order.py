# Copyright 2013-2016 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016 Antiun Ingenieria S.L. - Antonio Espinosa
# Copyright 2021 Tecnativa - Carlos Roca
# Copyright 2014-2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
import re

from lxml import etree, objectify

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError

try:
    from unidecode import unidecode
except ImportError:
    unidecode = None

logger = logging.getLogger(__name__)


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    sepa = fields.Boolean(compute="_compute_sepa", string="SEPA Payment")
    sepa_payment_method = fields.Boolean(
        compute="_compute_sepa",
        string="SEPA Payment Method",
    )
    show_warning_not_sepa = fields.Boolean(compute="_compute_sepa")
    charge_bearer = fields.Selection(
        [
            ("SLEV", "Following Service Level"),
            ("SHAR", "Shared"),
            ("CRED", "Borne by Creditor"),
            ("DEBT", "Borne by Debtor"),
        ],
        default="SLEV",
        readonly=True,
        states={"draft": [("readonly", False)], "open": [("readonly", False)]},
        tracking=True,
        help="Following service level : transaction charges are to be "
        "applied following the rules agreed in the service level "
        "and/or scheme (SEPA Core messages must use this). Shared : "
        "transaction charges on the debtor side are to be borne by "
        "the debtor, transaction charges on the creditor side are to "
        "be borne by the creditor. Borne by creditor : all "
        "transaction charges are to be borne by the creditor. Borne "
        "by debtor : all transaction charges are to be borne by the "
        "debtor.",
    )
    batch_booking = fields.Boolean(
        readonly=True,
        states={"draft": [("readonly", False)], "open": [("readonly", False)]},
        tracking=True,
        help="If true, the bank statement will display only one debit "
        "line for all the wire transfers of the SEPA XML file ; if "
        "false, the bank statement will display one debit line per wire "
        "transfer of the SEPA XML file.",
    )

    @api.model
    def _sepa_iban_prefix_list(self):
        # List of IBAN prefixes (not country codes !)
        # Source: https://www.europeanpaymentscouncil.eu/sites/default/files/kb/file/2023-01/EPC409-09%20EPC%20List%20of%20SEPA%20Scheme%20Countries%20v4.0_0.pdf  # noqa: B950
        # Some countries use IBAN but are not part of the SEPA zone
        # example: Turkey, Madagascar, Tunisia, etc.
        return [
            "AD",
            "AT",
            "BE",
            "BG",
            "ES",
            "HR",
            "CY",
            "CZ",
            "DK",
            "EE",
            "FI",
            "FR",
            "DE",
            "GI",
            "GR",
            "GB",
            "HU",
            "IS",
            "IE",
            "IT",
            "LV",
            "LI",
            "LT",
            "LU",
            "PT",
            "MT",
            "MC",
            "NL",
            "NO",
            "PL",
            "RO",
            "SM",
            "SK",
            "SI",
            "SE",
            "CH",
            "VA",
        ]

    @api.depends(
        "payment_mode_id",
        "company_partner_bank_id.acc_type",
        "company_partner_bank_id.sanitized_acc_number",
        "payment_line_ids.currency_id",
        "payment_line_ids.partner_bank_id.acc_type",
        "payment_line_ids.partner_bank_id.sanitized_acc_number",
    )
    def _compute_sepa(self):
        eur = self.env.ref("base.EUR")
        sepa_list = self._sepa_iban_prefix_list()
        for order in self:
            sepa_payment_method = False
            sepa = False
            warn_not_sepa = False
            payment_method = order.payment_mode_id.payment_method_id
            if payment_method.pain_version:
                sepa_payment_method = True
                sepa = True
                if (
                    order.company_partner_bank_id
                    and order.company_partner_bank_id.acc_type != "iban"
                ):
                    sepa = False
                if (
                    order.company_partner_bank_id
                    and order.company_partner_bank_id.sanitized_acc_number[:2]
                    not in sepa_list
                ):
                    sepa = False
                for pline in order.payment_line_ids:
                    if pline.currency_id != eur:
                        sepa = False
                        break
                    if (
                        pline.partner_bank_id
                        and pline.partner_bank_id.acc_type != "iban"
                    ):
                        sepa = False
                        break
                    if (
                        pline.partner_bank_id
                        and pline.partner_bank_id.sanitized_acc_number[:2]
                        not in sepa_list
                    ):
                        sepa = False
                        break
                sepa = order._compute_sepa_final_hook(sepa)
                if not sepa and payment_method.warn_not_sepa:
                    warn_not_sepa = True
            order.sepa = sepa
            order.sepa_payment_method = sepa_payment_method
            order.show_warning_not_sepa = warn_not_sepa

    def _compute_sepa_final_hook(self, sepa):
        self.ensure_one()
        return sepa

    @api.model
    def _prepare_field(
        self, field_name, value, max_size, gen_args, raise_if_oversized=False
    ):
        if gen_args is None:
            gen_args = {}
        if not value:
            raise UserError(
                _(
                    "Error in the generation of the XML payment file: "
                    "'%s' is empty. It should have a non-null value."
                )
                % field_name
            )
        if not isinstance(value, str):
            raise UserError(
                _(
                    "Error in the generation of the XML payment file: "
                    "'%(field)s' should be a string, "
                    "but it is %(value_type)s (value: %(value)s).",
                    field=field_name,
                    value_type=type(value),
                    value=value,
                )
            )

        # SEPA uses XML ; XML = UTF-8 ; UTF-8 = support for all characters
        # But we are dealing with banks... with old software that don't support UTF-8 !
        # cf section 1.4 "Character set" of the SEPA Credit Transfer
        # Scheme Customer-to-bank guidelines
        # Allowed caracters are: a-z A-Z 0-9 / - ? : ( ) . , ' + space
        if gen_args.get("convert_to_ascii"):
            value = unidecode(value)
            value = re.sub(r"[^a-zA-Z0-9/\-\?:\(\)\.,\'\+\s]", "-", value)

        if max_size and len(value) > max_size:
            if raise_if_oversized:
                raise UserError(
                    _(
                        "Error in the generation of the XML payment file: "
                        "'%(field_name)s' with value '%(value)s' has %(count)s caracters, "
                        "but the maximum is %(max_size)s caracters.",
                        field_name=field_name,
                        value=value,
                        count=len(value),
                        max_size=max_size,
                    )
                )
            else:
                value = value[:max_size]
        return value

    @api.model
    def _validate_xml(self, xml_bytes, gen_args):
        xsd_etree_obj = etree.parse(tools.file_open(gen_args["pain_xsd_file"]))
        official_pain_schema = etree.XMLSchema(xsd_etree_obj)

        try:
            root_to_validate = etree.fromstring(xml_bytes)
            official_pain_schema.assertValid(root_to_validate)
        except Exception as e:
            logger.warning("The XML file is invalid against the XML Schema Definition")
            logger.warning(xml_bytes)
            logger.warning(e)
            raise UserError(
                _(
                    "The generated XML file is not valid against the official "
                    "XML Schema Definition. The generated XML file and the "
                    "full error have been written in the server logs. Here "
                    "is the error, which may give you an idea on the cause "
                    "of the problem : %s"
                )
                % str(e)
            ) from None

    def _finalize_sepa_file_creation(self, xml_root, gen_args):
        objectify.deannotate(xml_root)
        xml_bytes = etree.tostring(
            xml_root, pretty_print=True, encoding="UTF-8", xml_declaration=True
        )
        # I didn't find a way to remove py:pytype and xmlns:py while keeping
        # xmlns:xsi and xmlns
        # If I use objectify.deannotate(xml_root, cleanup_namespaces=True),
        # it will remove all the unused namespaces,
        # so it also removes xmlns:xsi and xmlns.
        # The only solution I found is to manually remove xmlns:py in the output string
        xml_string = xml_bytes.decode("utf-8")
        xml_string = xml_string.replace(
            ''' xmlns:py="http://codespeak.net/lxml/objectify/pytype"''', ""
        )
        xml_bytes = xml_string.encode("utf-8")
        logger.debug(
            "Generated SEPA XML file in format %s below" % gen_args["pain_flavor"]
        )
        logger.debug(xml_bytes)
        self._validate_xml(xml_bytes, gen_args)

        filename = "{}{}.xml".format(gen_args["file_prefix"], self.name)
        return (xml_bytes, filename)

    def _generate_pain_nsmap(self):
        self.ensure_one()
        pain_flavor = self.payment_mode_id.payment_method_id.pain_version
        nsmap = {
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
            None: "urn:iso:std:iso:20022:tech:xsd:%s" % pain_flavor,
        }
        return nsmap

    def _generate_pain_attrib(self):
        self.ensure_one()
        return {}

    @api.model
    def _generate_group_header_block(self, parent_node, gen_args):
        group_header = objectify.SubElement(parent_node, "GrpHdr")
        group_header.MsgId = self._prepare_field(
            "Message Identification", self.name, 35, gen_args, raise_if_oversized=True
        )
        group_header.CreDtTm = fields.Datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        # Initialize value value ; will be updated in another method
        group_header.NbOfTxs = 0
        group_header.CtrlSum = 0.00
        self._generate_initiating_party_block(group_header, gen_args)
        return group_header

    @api.model
    def _generate_start_payment_info_block(
        self,
        parent_node,
        payment_info_ident,
        priority,
        local_instrument,
        category_purpose,
        sequence_type,
        requested_date,
        gen_args,
    ):
        payment_info = objectify.SubElement(parent_node, "PmtInf")
        payment_info.PmtInfId = self._prepare_field(
            "Payment Information Identification",
            payment_info_ident,
            35,
            gen_args,
            raise_if_oversized=True,
        )
        payment_info.PmtMtd = gen_args["payment_method"]
        payment_info.BtchBookg = str(self.batch_booking).lower()
        # The "SEPA Customer-to-bank
        # Implementation guidelines" for SCT and SDD says that control sum
        # and nb_of_transactions should be present
        # at both "group header" level and "payment info" level
        payment_info.NbOfTxs = 0
        payment_info.CtrlSum = 0.0
        payment_type_info = objectify.SubElement(payment_info, "PmtTpInf")
        if priority and gen_args["payment_method"] != "DD":
            payment_type_info.InstrPrty = priority
        if self.sepa:
            service_level = objectify.SubElement(payment_type_info, "SvcLvl")
            service_level.Cd = "SEPA"
        if local_instrument:
            local_instrument_root = objectify.SubElement(payment_type_info, "LclInstrm")
            if gen_args.get("local_instrument_type") == "proprietary":
                local_instrument_root.Prtry = local_instrument
            else:
                local_instrument_root.Cd = local_instrument
        if sequence_type:
            payment_type_info.SeqTp = sequence_type
        if category_purpose:
            category_purpose_node = objectify.SubElement(payment_type_info, "CtgyPurp")
            category_purpose_node.Cd = category_purpose
        if gen_args["payment_method"] == "DD":
            payment_info.ReqdColltnDt = requested_date.strftime("%Y-%m-%d")
        else:
            payment_info.ReqdExctnDt = requested_date.strftime("%Y-%m-%d")
        return payment_info

    @api.model
    def _must_have_initiating_party(self, gen_args):
        """This method is designed to be inherited in localization modules for
        countries in which the initiating party is required"""
        return False

    @api.model
    def _generate_initiating_party_block(self, parent_node, gen_args):
        my_company_name = self._prepare_field(
            "Company Name",
            self.company_partner_bank_id.partner_id.name,
            gen_args.get("name_maxsize"),
            gen_args,
        )
        initiating_party = objectify.SubElement(parent_node, "InitgPty")
        initiating_party.Nm = my_company_name
        initiating_party_identifier = (
            self.payment_mode_id.initiating_party_identifier
            or self.payment_mode_id.company_id.initiating_party_identifier
        )
        initiating_party_issuer = (
            self.payment_mode_id.initiating_party_issuer
            or self.payment_mode_id.company_id.initiating_party_issuer
        )
        initiating_party_scheme = (
            self.payment_mode_id.initiating_party_scheme
            or self.payment_mode_id.company_id.initiating_party_scheme
        )
        # in pain.008.001.02.ch.01.xsd files they use
        # initiating_party_identifier but not initiating_party_issuer
        if initiating_party_identifier:
            iniparty_id = objectify.SubElement(initiating_party, "Id")
            iniparty_org_id = objectify.SubElement(iniparty_id, "OrgId")
            iniparty_org_other = objectify.SubElement(iniparty_org_id, "Othr")
            iniparty_org_other.Id = initiating_party_identifier
            if initiating_party_scheme:
                iniparty_org_other_scheme = objectify.SubElement(
                    iniparty_org_other, "SchmeNm"
                )
                iniparty_org_other_scheme.Prtry = initiating_party_scheme
            if initiating_party_issuer:
                iniparty_org_other.Issr = initiating_party_issuer
        elif self._must_have_initiating_party(gen_args):
            raise UserError(
                _(
                    "Missing 'Initiating Party Issuer' and/or "
                    "'Initiating Party Identifier' for the company '%s'. "
                    "Both fields must have a value."
                )
                % self.company_id.name
            )

    @api.model
    def _generate_party_agent(
        self, parent_node, party_type, order, partner_bank, gen_args, bank_line=None
    ):
        """Generate the piece of the XML file corresponding to BIC
        This code is mutualized between TRF and DD
        Starting from Feb 1st 2016, we should be able to do
        cross-border SEPA transfers without BIC, cf
        http://www.europeanpaymentscouncil.eu/index.cfm/
        sepa-credit-transfer/iban-and-bic/
        In some localization (l10n_ch_sepa for example), they need the
        bank_line argument"""
        assert order in ("B", "C"), "Order can be 'B' or 'C'"
        if partner_bank.bank_bic:
            party_agent = objectify.SubElement(parent_node, f"{party_type}Agt")
            party_agent_institution = objectify.SubElement(party_agent, "FinInstnId")
            setattr(
                party_agent_institution,
                gen_args.get("bic_xml_tag"),
                partner_bank.bank_bic,
            )
        else:
            if order == "B" or (order == "C" and gen_args["payment_method"] == "DD"):
                party_agent = objectify.SubElement(parent_node, "%sAgt" % party_type)
                party_agent_institution = objectify.SubElement(
                    party_agent, "FinInstnId"
                )
                party_agent_other = objectify.SubElement(
                    party_agent_institution, "Othr"
                )
                party_agent_other.Id = "NOTPROVIDED"
            # for Credit Transfers, in the 'C' block, if BIC is not provided,
            # we should not put the 'Creditor Agent' block at all,
            # as per the guidelines of the EPC

    @api.model
    def _generate_party_id(self, parent_node, party_type, partner):
        """Generate an Id element for partner inside the parent node.
        party_type can currently be Cdtr or Dbtr. Notably, the initiating
        party orgid is generated with another mechanism and configured
        at the company or payment mode level.
        """
        return

    @api.model
    def _generate_party_acc_number(
        self, parent_node, party_type, order, partner_bank, gen_args, bank_line=None
    ):
        party_account = objectify.SubElement(parent_node, f"{party_type}Acct")
        party_account_id = objectify.SubElement(party_account, "Id")
        if partner_bank.acc_type == "iban":
            party_account_id.IBAN = partner_bank.sanitized_acc_number
        else:
            party_account_other = objectify.SubElement(party_account_id, "Othr")
            party_account_other.Id = partner_bank.sanitized_acc_number
        if party_type == "Dbtr" and partner_bank.currency_id:
            party_account.Ccy = partner_bank.currency_id.name

    @api.model
    def _generate_address_block(self, parent_node, partner, gen_args):
        """Generate the piece of the XML corresponding to PstlAdr"""
        if partner.country_id:
            postal_address = objectify.SubElement(parent_node, "PstlAdr")
            postal_address.Ctry = partner.country_id.code
            if partner.street:
                postal_address.AdrLine = self._prepare_field(
                    "Address Line1", partner.street, 70, gen_args
                )
            if (
                gen_args.get("pain_flavor").startswith("pain.001.001.")
                or gen_args.get("pain_flavor").startswith("pain.008.001.")
            ) and (partner.zip or partner.city):
                if partner.zip:
                    val = self._prepare_field("zip", partner.zip, 70, gen_args)
                else:
                    val = ""
                if partner.city:
                    val += " " + self._prepare_field("city", partner.city, 70, gen_args)
                postal_address.AdrLine = val

    @api.model
    def _generate_party_block(
        self, parent_node, party_type, order, partner_bank, gen_args, bank_line=None
    ):
        """Generate the piece of the XML file corresponding to Name+IBAN+BIC
        This code is mutualized between TRF and DD
        In some localization (l10n_ch_sepa for example), they need the
        bank_line argument"""
        assert order in ("B", "C"), "Order can be 'B' or 'C'"
        party_type_label = _("Partner name")
        if party_type == "Cdtr":
            party_type_label = _("Creditor name")
        elif party_type == "Dbtr":
            party_type_label = _("Debtor name")
        partner_name = partner_bank.acc_holder_name or partner_bank.partner_id.name
        party_name = self._prepare_field(
            party_type_label, partner_name, gen_args.get("name_maxsize"), gen_args
        )
        # At C level, the order is : BIC, Name, IBAN
        # At B level, the order is : Name, IBAN, BIC
        if order == "C":
            self._generate_party_agent(
                parent_node,
                party_type,
                order,
                partner_bank,
                gen_args,
                bank_line=bank_line,
            )
        party = objectify.SubElement(parent_node, party_type)
        party.Nm = party_name
        partner = partner_bank.partner_id

        self._generate_address_block(party, partner, gen_args)

        self._generate_party_id(party, party_type, partner)

        self._generate_party_acc_number(
            parent_node, party_type, order, partner_bank, gen_args, bank_line=bank_line
        )

        if order == "B":
            self._generate_party_agent(
                parent_node,
                party_type,
                order,
                partner_bank,
                gen_args,
                bank_line=bank_line,
            )

    @api.model
    def _generate_remittance_info_block(self, parent_node, line, gen_args):
        remittance_info = objectify.SubElement(parent_node, "RmtInf")
        communication_type = line.payment_line_ids[:1].communication_type
        if communication_type == "free":
            remittance_info.Ustrd = self._prepare_field(
                "Remittance Unstructured Information",
                line.payment_reference,
                140,
                gen_args,
            )
        elif communication_type == "structured":
            remittance_info_structured = objectify.SubElement(remittance_info, "Strd")
            creditor_ref_information = objectify.SubElement(
                remittance_info_structured, "CdtrRefInf"
            )
            if gen_args.get("structured_remittance_issuer", True):
                creditor_ref_info_type = objectify.SubElement(
                    creditor_ref_information, "Tp"
                )
                creditor_ref_info_type_or = objectify.SubElement(
                    creditor_ref_info_type, "CdOrPrtry"
                )
                creditor_ref_info_type_or.Cd = "SCOR"
                creditor_ref_info_type.Issr = "ISO"

            ref_tag = "Ref"

            setattr(
                creditor_ref_information,
                ref_tag,
                self._prepare_field(
                    "Creditor Structured Reference",
                    line.payment_reference,
                    35,
                    gen_args,
                    raise_if_oversized=True,
                ),
            )

    @api.model
    def _generate_creditor_scheme_identification(
        self,
        parent_node,
        identification,
        identification_label,
        scheme_name_proprietary,
        gen_args,
    ):
        csi_root = objectify.SubElement(parent_node, "CdtrSchmeId")
        csi_id = objectify.SubElement(csi_root, "Id")
        csi_privateid = objectify.SubElement(csi_id, "PrvtId")
        csi_other = objectify.SubElement(csi_privateid, "Othr")
        csi_other.Id = self._prepare_field(
            identification_label, identification, 35, gen_args, raise_if_oversized=True
        )
        csi_scheme_name = objectify.SubElement(csi_other, "SchmeNm")
        csi_scheme_name.Prtry = scheme_name_proprietary

    def _generate_charge_bearer(self, parent_node):
        self.ensure_one()
        if self.sepa:
            parent_node.ChrgBr = "SLEV"
        else:
            parent_node.ChrgBr = self.charge_bearer

    def _format_control_sum(self, control_sum):
        self.ensure_one()
        decimal_places = max(
            [line.currency_id.decimal_places for line in self.payment_line_ids]
        )
        fmt = f"%.{decimal_places}f"
        control_sum_str = fmt % control_sum
        return control_sum_str
