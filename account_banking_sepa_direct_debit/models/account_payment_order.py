# Copyright 2020 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# Copyright 2018-2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import objectify

from odoo import _, models
from odoo.exceptions import UserError


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    def generate_payment_file(self):
        """Creates the SEPA Direct Debit file. That's the important code !"""
        self.ensure_one()
        if self.payment_method_id.code != "sepa_direct_debit":
            return super().generate_payment_file()
        pain_flavor = self.payment_method_id.pain_version
        # We use pain_flavor.startswith('pain.008.001.xx')
        # to support country-specific extensions such as
        # pain.008.001.02.ch.01 (cf l10n_ch_sepa)
        if pain_flavor.startswith(("pain.008.001.02", "pain.008.003.02")):
            bic_xml_tag = "BIC"
            name_maxsize = 70
        elif pain_flavor.startswith(("pain.008.001.03", "pain.008.001.04")):
            bic_xml_tag = "BICFI"
            name_maxsize = 140
        else:
            raise UserError(
                _(
                    "Payment Type Code '%s' is not supported. The only "
                    "Payment Type Code supported for SEPA Direct Debit are "
                    "'pain.008.001.02', 'pain.008.001.03' and "
                    "'pain.008.001.04'."
                )
                % pain_flavor
            )
        pay_method = self.payment_mode_id.payment_method_id
        xsd_file = pay_method._get_xsd_file_path()
        gen_args = {
            "bic_xml_tag": bic_xml_tag,
            "name_maxsize": name_maxsize,
            "convert_to_ascii": pay_method.convert_to_ascii,
            "payment_method": "DD",
            "file_prefix": "sdd_",
            "pain_flavor": pain_flavor,
            "pain_xsd_file": xsd_file,
        }
        nsmap = self._generate_pain_nsmap()
        attrib = self._generate_pain_attrib()
        xml_root = objectify.Element("Document", nsmap=nsmap, attrib=attrib)
        pain_root = objectify.SubElement(xml_root, "CstmrDrctDbtInitn")
        # A. Group header
        group_header = self._generate_group_header_block(pain_root, gen_args)
        transactions_count_a = 0
        amount_control_sum_a = 0.0
        lines_per_group = {}
        # key = (requested_date, priority, sequence type)
        # value = list of lines as objects
        for line in self.payment_ids:
            payment_line = line.payment_line_ids[:1]
            priority = payment_line.priority
            categ_purpose = payment_line.category_purpose
            scheme = payment_line.mandate_id.scheme
            if payment_line.mandate_id.type == "oneoff":
                seq_type = "OOFF"
            elif payment_line.mandate_id.type == "recurrent":
                seq_type_map = {"recurring": "RCUR", "first": "FRST", "final": "FNAL"}
                seq_type_label = payment_line.mandate_id.recurrent_sequence_type
                assert seq_type_label is not False
                seq_type = seq_type_map[seq_type_label]
            else:
                raise UserError(
                    _(
                        "Invalid mandate type in '%s'. Valid ones are 'Recurrent' "
                        "or 'One-Off'."
                    )
                    % payment_line.mandate_id.unique_mandate_reference
                )
            # The field line.date is the requested payment date
            # taking into account the 'date_preferred' setting
            # cf account_banking_payment_export/models/account_payment.py
            # in the inherit of action_open()
            key = (line.date, priority, categ_purpose, seq_type, scheme)
            if key in lines_per_group:
                lines_per_group[key].append(line)
            else:
                lines_per_group[key] = [line]

        for (
            (requested_date, priority, categ_purpose, sequence_type, scheme),
            lines,
        ) in list(lines_per_group.items()):
            # B. Payment info
            payment_info = self._generate_start_payment_info_block(
                pain_root,
                f"{self.name}-{sequence_type}-{requested_date.strftime('%Y%m%d')}-"
                f"{priority}-{categ_purpose or 'NOpu'}",
                priority,
                scheme,
                categ_purpose,
                sequence_type,
                requested_date,
                gen_args,
            )

            self._generate_party_block(
                payment_info, "Cdtr", "B", self.company_partner_bank_id, gen_args
            )
            self._generate_charge_bearer(payment_info)
            sepa_creditor_identifier = (
                self.payment_mode_id.sepa_creditor_identifier
                or self.company_id.sepa_creditor_identifier
            )
            if not sepa_creditor_identifier:
                raise UserError(
                    _(
                        "Missing SEPA Creditor Identifier on company %(company)s "
                        "(or on payment mode %(payment_mode)s).",
                        company=self.company_id.display_name,
                        payment_mode=self.payment_mode_id.display_name,
                    )
                )
            self._generate_creditor_scheme_identification(
                payment_info,
                sepa_creditor_identifier,
                "SEPA Creditor Identifier",
                "SEPA",
                gen_args,
            )
            transactions_count_b = 0
            amount_control_sum_b = 0.0
            for line in lines:
                transactions_count_a += 1
                transactions_count_b += 1
                # C. Direct Debit Transaction Info
                dd_transaction_info = objectify.SubElement(payment_info, "DrctDbtTxInf")
                payment_identification = objectify.SubElement(
                    dd_transaction_info, "PmtId"
                )
                payment_identification.InstrId = self._prepare_field(
                    "Instruction Identification", str(line.move_id.id), 35, gen_args
                )
                payment_identification.EndToEndId = self._prepare_field(
                    "End to End Identification", str(line.move_id.id), 35, gen_args
                )
                dd_transaction_info.InstdAmt = line.currency_id._pain_format(
                    line.amount
                )
                dd_transaction_info.InstdAmt.set("Ccy", line.currency_id.name)
                amount_control_sum_a += line.amount
                amount_control_sum_b += line.amount
                dd_transaction = objectify.SubElement(dd_transaction_info, "DrctDbtTx")
                mandate_related_info = objectify.SubElement(
                    dd_transaction, "MndtRltdInf"
                )
                mandate = line.payment_line_ids[:1].mandate_id
                mandate_related_info.MndtId = self._prepare_field(
                    "Unique Mandate Reference",
                    mandate.unique_mandate_reference,
                    35,
                    gen_args,
                    raise_if_oversized=True,
                )
                mandate_related_info.DtOfSgntr = mandate.signature_date.strftime(
                    "%Y-%m-%d"
                )
                if sequence_type == "FRST" and mandate.last_debit_date:
                    mandate_related_info.AmdmntInd = "true"
                    amendment_info_details = objectify.SubElement(
                        mandate_related_info, "AmdmntInfDtls"
                    )
                    ori_debtor_account = objectify.SubElement(
                        amendment_info_details, "OrgnlDbtrAcct"
                    )
                    ori_debtor_account_id = objectify.SubElement(
                        ori_debtor_account, "Id"
                    )
                    ori_debtor_agent_other = objectify.SubElement(
                        ori_debtor_account_id, "Othr"
                    )
                    ori_debtor_agent_other.Id = "SMNDA"
                    # Until 20/11/2016, SMNDA meant
                    # "Same Mandate New Debtor Agent"
                    # After 20/11/2016, SMNDA means
                    # "Same Mandate New Debtor Account"

                self._generate_party_block(
                    dd_transaction_info,
                    "Dbtr",
                    "C",
                    line.partner_bank_id,
                    gen_args,
                    line,
                )
                payment_line = line.payment_line_ids[0]
                payment_line._generate_purpose(dd_transaction_info)
                payment_line._generate_regulatory_reporting(
                    dd_transaction_info, gen_args
                )
                self._generate_remittance_info_block(
                    dd_transaction_info, line, gen_args
                )

            payment_info.NbOfTxs = str(transactions_count_b)
            payment_info.CtrlSum = self._format_control_sum(amount_control_sum_b)
        group_header.NbOfTxs = str(transactions_count_a)
        group_header.CtrlSum = self._format_control_sum(amount_control_sum_a)

        return self._finalize_sepa_file_creation(xml_root, gen_args)

    def generated2uploaded(self):
        """Write 'last debit date' on mandates
        Set mandates from first to recurring
        Set oneoff mandates to expired
        """
        # I call super() BEFORE updating the sequence_type
        # from first to recurring, so that the account move
        # is generated BEFORE, which will allow the split
        # of the account move per sequence_type
        res = super().generated2uploaded()
        abmo = self.env["account.banking.mandate"]
        for order in self:
            to_expire_mandates = abmo.browse([])
            first_mandates = abmo.browse([])
            all_mandates = abmo.browse([])
            for payment in order.payment_ids:
                mandate = payment.payment_line_ids.mandate_id
                if mandate in all_mandates:
                    continue
                all_mandates += mandate
                if mandate.type == "oneoff":
                    to_expire_mandates += mandate
                elif mandate.type == "recurrent":
                    seq_type = mandate.recurrent_sequence_type
                    if seq_type == "final":
                        to_expire_mandates += mandate
                    elif seq_type == "first":
                        first_mandates += mandate
            all_mandates.write({"last_debit_date": order.date_generated})
            to_expire_mandates.write({"state": "expired"})
            first_mandates.write({"recurrent_sequence_type": "recurring"})
            for first_mandate in first_mandates:
                first_mandate.message_post(
                    body=_(
                        "Automatically switched from <b>First</b> to "
                        "<b>Recurring</b> when the debit order "
                        "<a href=# data-oe-model=account.payment.order "
                        "data-oe-id=%d>{}</a> has been marked as uploaded."
                    ).format(order.id, order.name)
                )
        return res
