# Copyright 2020 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# Copyright 2018-2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree
from markupsafe import Markup

from odoo import _, exceptions, fields, models
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
        if pain_flavor.startswith("pain.008.001.02"):
            bic_xml_tag = "BIC"
            name_maxsize = 70
            root_xml_tag = "CstmrDrctDbtInitn"
        elif pain_flavor.startswith("pain.008.003.02"):
            bic_xml_tag = "BIC"
            name_maxsize = 70
            root_xml_tag = "CstmrDrctDbtInitn"
        elif pain_flavor.startswith("pain.008.001.03"):
            bic_xml_tag = "BICFI"
            name_maxsize = 140
            root_xml_tag = "CstmrDrctDbtInitn"
        elif pain_flavor.startswith("pain.008.001.04"):
            bic_xml_tag = "BICFI"
            name_maxsize = 140
            root_xml_tag = "CstmrDrctDbtInitn"
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
        xsd_file = pay_method.get_xsd_file_path()
        gen_args = {
            "bic_xml_tag": bic_xml_tag,
            "name_maxsize": name_maxsize,
            "convert_to_ascii": pay_method.convert_to_ascii,
            "payment_method": "DD",
            "file_prefix": "sdd_",
            "pain_flavor": pain_flavor,
            "pain_xsd_file": xsd_file,
        }
        nsmap = self.generate_pain_nsmap()
        attrib = self.generate_pain_attrib()
        xml_root = etree.Element("Document", nsmap=nsmap, attrib=attrib)
        pain_root = etree.SubElement(xml_root, root_xml_tag)
        # A. Group header
        (
            group_header,
            nb_of_transactions_a,
            control_sum_a,
        ) = self.generate_group_header_block(pain_root, gen_args)
        transactions_count_a = 0
        amount_control_sum_a = 0.0
        lines_per_group = {}
        # key = (requested_date, priority, sequence type)
        # value = list of lines as objects
        for line in self.payment_ids:
            transactions_count_a += 1
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
                raise exceptions.UserError(
                    _(
                        "Invalid mandate type in '%s'. Valid ones are 'Recurrent' "
                        "or 'One-Off'"
                    )
                    % payment_line.mandate_id.unique_mandate_reference
                )
            # The field line.payment_line_date is the requested payment date
            key = (line.payment_line_date, priority, categ_purpose, seq_type, scheme)
            if key in lines_per_group:
                lines_per_group[key].append(line)
            else:
                lines_per_group[key] = [line]

        for (
            (requested_date, priority, categ_purpose, sequence_type, scheme),
            lines,
        ) in list(lines_per_group.items()):
            requested_date = fields.Date.to_string(requested_date)
            # B. Payment info
            (
                payment_info,
                nb_of_transactions_b,
                control_sum_b,
            ) = self.generate_start_payment_info_block(
                pain_root,
                "self.name + '-' + "
                "sequence_type + '-' + requested_date.replace('-', '')  "
                "+ '-' + priority + '-' + category_purpose",
                priority,
                scheme,
                categ_purpose,
                sequence_type,
                requested_date,
                {
                    "self": self,
                    "sequence_type": sequence_type,
                    "priority": priority,
                    "category_purpose": categ_purpose or "NOcateg",
                    "requested_date": requested_date,
                },
                gen_args,
            )

            self.generate_party_block(
                payment_info, "Cdtr", "B", self.company_partner_bank_id, gen_args
            )
            charge_bearer = etree.SubElement(payment_info, "ChrgBr")
            if self.sepa:
                charge_bearer_text = "SLEV"
            else:
                charge_bearer_text = self.charge_bearer
            charge_bearer.text = charge_bearer_text
            creditor_scheme_identification = etree.SubElement(
                payment_info, "CdtrSchmeId"
            )
            self.generate_creditor_scheme_identification(
                creditor_scheme_identification,
                "self.payment_mode_id.sepa_creditor_identifier or "
                "self.company_id.sepa_creditor_identifier",
                "SEPA Creditor Identifier",
                {"self": self},
                "SEPA",
                gen_args,
            )
            transactions_count_b = 0
            amount_control_sum_b = 0.0
            for line in lines:
                transactions_count_b += 1
                # C. Direct Debit Transaction Info
                dd_transaction_info = etree.SubElement(payment_info, "DrctDbtTxInf")
                payment_identification = etree.SubElement(dd_transaction_info, "PmtId")
                instruction_identification = etree.SubElement(
                    payment_identification, "InstrId"
                )
                instruction_identification.text = self._prepare_field(
                    "Instruction Identification",
                    "str(line.id)",
                    {"line": line},
                    35,
                    gen_args=gen_args,
                )
                end2end_identification = etree.SubElement(
                    payment_identification, "EndToEndId"
                )
                end2end_identification.text = self._prepare_field(
                    "End to End Identification",
                    "str(line.id)",
                    {"line": line},
                    35,
                    gen_args=gen_args,
                )
                currency_name = self._prepare_field(
                    "Currency Code",
                    "line.currency_id.name",
                    {"line": line},
                    3,
                    gen_args=gen_args,
                )
                instructed_amount = etree.SubElement(
                    dd_transaction_info, "InstdAmt", Ccy=currency_name
                )
                instructed_amount.text = f"{line.amount:.2f}"
                amount_control_sum_a += line.amount
                amount_control_sum_b += line.amount
                dd_transaction = etree.SubElement(dd_transaction_info, "DrctDbtTx")
                mandate_related_info = etree.SubElement(dd_transaction, "MndtRltdInf")
                mandate_identification = etree.SubElement(
                    mandate_related_info, "MndtId"
                )
                mandate = line.payment_line_ids[:1].mandate_id
                mandate_identification.text = self._prepare_field(
                    "Unique Mandate Reference",
                    "mandate.unique_mandate_reference",
                    {"mandate": mandate},
                    35,
                    gen_args=gen_args,
                )
                mandate_signature_date = etree.SubElement(
                    mandate_related_info, "DtOfSgntr"
                )
                mandate_signature_date.text = self._prepare_field(
                    "Mandate Signature Date",
                    "signature_date",
                    {
                        "line": line,
                        "signature_date": fields.Date.to_string(mandate.signature_date),
                    },
                    10,
                    gen_args=gen_args,
                )
                if sequence_type == "FRST" and mandate.last_debit_date:
                    amendment_indicator = etree.SubElement(
                        mandate_related_info, "AmdmntInd"
                    )
                    amendment_indicator.text = "true"
                    amendment_info_details = etree.SubElement(
                        mandate_related_info, "AmdmntInfDtls"
                    )
                    ori_debtor_account = etree.SubElement(
                        amendment_info_details, "OrgnlDbtrAcct"
                    )
                    ori_debtor_account_id = etree.SubElement(ori_debtor_account, "Id")
                    ori_debtor_agent_other = etree.SubElement(
                        ori_debtor_account_id, "Othr"
                    )
                    ori_debtor_agent_other_id = etree.SubElement(
                        ori_debtor_agent_other, "Id"
                    )
                    ori_debtor_agent_other_id.text = "SMNDA"
                    # Until 20/11/2016, SMNDA meant
                    # "Same Mandate New Debtor Agent"
                    # After 20/11/2016, SMNDA means
                    # "Same Mandate New Debtor Account"

                self.generate_party_block(
                    dd_transaction_info,
                    "Dbtr",
                    "C",
                    line.partner_bank_id,
                    gen_args,
                    line,
                )
                line_purpose = line.payment_line_ids[:1].purpose
                if line_purpose:
                    purpose = etree.SubElement(dd_transaction_info, "Purp")
                    etree.SubElement(purpose, "Cd").text = line_purpose

                self.generate_remittance_info_block(dd_transaction_info, line, gen_args)

            nb_of_transactions_b.text = str(transactions_count_b)
            control_sum_b.text = f"{amount_control_sum_b:.2f}"
        nb_of_transactions_a.text = str(transactions_count_a)
        control_sum_a.text = f"{amount_control_sum_a:.2f}"

        return self.finalize_sepa_file_creation(xml_root, gen_args)

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
                    body=Markup(
                        _(
                            "Automatically switched from <b>First</b> to "
                            "<b>Recurring</b> when the debit order "
                            "<a href=# data-oe-model=account.payment.order "
                            "data-oe-id=%(id)d>%(name)s</a> "
                            "has been marked as uploaded.",
                            id=order.id,
                            name=order.name,
                        )
                    )
                )
        return res
