# -*- coding: utf-8 -*-
# © 2010-2016 Akretion (www.akretion.com)
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, _
from odoo.exceptions import UserError
from lxml import etree


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    @api.model
    def _get_line_key(self, line):
        # The field line.date is the requested payment date
        # taking into account the 'date_prefered' setting
        # cf account_banking_payment_export/models/account_payment.py
        # in the inherit of action_open()
        return (
            line.date,
            line.priority,
            line.local_instrument,
            line.category_purpose
        )

    @api.multi
    def generate_payment_file(self):
        """Creates the SEPA Credit Transfer file. That's the important code!"""
        self.ensure_one()
        if self.payment_method_id.code != 'sepa_credit_transfer':
            return super(AccountPaymentOrder, self).generate_payment_file()

        pain_flavor = self.payment_method_id.pain_version
        if not pain_flavor:
            pain_flavor = 'pain.001.001.03'
        # We use pain_flavor.startswith('pain.001.001.xx')
        # to support country-specific extensions such as
        # pain.001.001.03.ch.02 (cf l10n_ch_sepa)
        if pain_flavor.startswith('pain.001.001.02'):
            bic_xml_tag = 'BIC'
            name_maxsize = 70
            root_xml_tag = 'pain.001.001.02'
        elif pain_flavor.startswith('pain.001.001.03'):
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
        elif pain_flavor.startswith('pain.001.001.04'):
            bic_xml_tag = 'BICFI'
            name_maxsize = 140
            root_xml_tag = 'CstmrCdtTrfInitn'
        elif pain_flavor.startswith('pain.001.001.05'):
            bic_xml_tag = 'BICFI'
            name_maxsize = 140
            root_xml_tag = 'CstmrCdtTrfInitn'
        # added pain.001.003.03 for German Banks
        # it is not in the offical ISO 20022 documentations, but nearly all
        # german banks are working with this instead 001.001.03
        elif pain_flavor == 'pain.001.003.03':
            bic_xml_tag = 'BIC'
            name_maxsize = 70
            root_xml_tag = 'CstmrCdtTrfInitn'
        else:
            raise UserError(
                _("PAIN version '%s' is not supported.") % pain_flavor)
        xsd_file = self.payment_method_id.get_xsd_file_path()
        gen_args = {
            'bic_xml_tag': bic_xml_tag,
            'name_maxsize': name_maxsize,
            'convert_to_ascii': self.payment_method_id.convert_to_ascii,
            'payment_method': 'TRF',
            'file_prefix': 'sct_',
            'pain_flavor': pain_flavor,
            'pain_xsd_file': xsd_file,
        }
        nsmap = self.generate_pain_nsmap()
        attrib = self.generate_pain_attrib()
        xml_root = etree.Element('Document', nsmap=nsmap, attrib=attrib)
        pain_root = etree.SubElement(xml_root, root_xml_tag)
        # A. Group header
        group_header, nb_of_transactions_a, control_sum_a = \
            self.generate_group_header_block(pain_root, gen_args)
        transactions_count_a = 0
        amount_control_sum_a = 0.0
        lines_per_group = {}
        # key = (requested_date, priority, local_instrument, categ_purpose)
        # values = list of lines as object
        for line in self.bank_line_ids:
            key = self._get_line_key(line)
            if key in lines_per_group:
                lines_per_group[key].append(line)
            else:
                lines_per_group[key] = [line]
        for block_info, lines in lines_per_group.items():
            requested_date, priority,\
                local_instrument, categ_purpose = block_info[:4]
            # B. Payment info
            payment_info, nb_of_transactions_b, control_sum_b = \
                self.generate_start_payment_info_block(
                    pain_root,
                    "self.name + '-' "
                    "+ requested_date.replace('-', '')  + '-' + priority + "
                    "'-' + local_instrument + '-' + category_purpose",
                    priority, local_instrument, categ_purpose,
                    False, requested_date, {
                        'self': self,
                        'priority': priority,
                        'requested_date': requested_date,
                        'local_instrument': local_instrument or 'NOinstr',
                        'category_purpose': categ_purpose or 'NOcateg',
                        'optional_args': block_info[4:]
                    }, gen_args)
            self.generate_party_block(
                payment_info, 'Dbtr', 'B',
                self.company_partner_bank_id, gen_args)
            charge_bearer = etree.SubElement(payment_info, 'ChrgBr')
            if self.sepa:
                charge_bearer_text = 'SLEV'
            else:
                charge_bearer_text = self.charge_bearer
            charge_bearer.text = charge_bearer_text
            transactions_count_b = 0
            amount_control_sum_b = 0.0
            for line in lines:
                transactions_count_a += 1
                transactions_count_b += 1
                # C. Credit Transfer Transaction Info
                credit_transfer_transaction_info = etree.SubElement(
                    payment_info, 'CdtTrfTxInf')
                payment_identification = etree.SubElement(
                    credit_transfer_transaction_info, 'PmtId')
                instruction_identification = etree.SubElement(
                    payment_identification, 'InstrId')
                instruction_identification.text = self._prepare_field(
                    'Instruction Identification', 'line.name',
                    {'line': line}, 35, gen_args=gen_args)
                end2end_identification = etree.SubElement(
                    payment_identification, 'EndToEndId')
                end2end_identification.text = self._prepare_field(
                    'End to End Identification', 'line.name',
                    {'line': line}, 35, gen_args=gen_args)
                currency_name = self._prepare_field(
                    'Currency Code', 'line.currency_id.name',
                    {'line': line}, 3, gen_args=gen_args)
                amount = etree.SubElement(
                    credit_transfer_transaction_info, 'Amt')
                instructed_amount = etree.SubElement(
                    amount, 'InstdAmt', Ccy=currency_name)
                instructed_amount.text = '%.2f' % line.amount_currency
                amount_control_sum_a += line.amount_currency
                amount_control_sum_b += line.amount_currency
                if not line.partner_bank_id:
                    raise UserError(
                        _("Bank account is missing on the bank payment line "
                            "of partner '%s' (reference '%s').")
                        % (line.partner_id.name, line.name))
                self.generate_party_block(
                    credit_transfer_transaction_info, 'Cdtr',
                    'C', line.partner_bank_id, gen_args, line)
                if line.purpose:
                    purpose = etree.SubElement(
                        credit_transfer_transaction_info, 'Purp')
                    etree.SubElement(purpose, 'Cd').text = line.purpose
                self.generate_remittance_info_block(
                    credit_transfer_transaction_info, line, gen_args)
            if not pain_flavor.startswith('pain.001.001.02'):
                nb_of_transactions_b.text = unicode(transactions_count_b)
                control_sum_b.text = '%.2f' % amount_control_sum_b
        if not pain_flavor.startswith('pain.001.001.02'):
            nb_of_transactions_a.text = unicode(transactions_count_a)
            control_sum_a.text = '%.2f' % amount_control_sum_a
        else:
            nb_of_transactions_a.text = unicode(transactions_count_a)
            control_sum_a.text = '%.2f' % amount_control_sum_a
        return self.finalize_sepa_file_creation(xml_root, gen_args)
