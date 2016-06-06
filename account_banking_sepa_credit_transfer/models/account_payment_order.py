# -*- coding: utf-8 -*-
# © 2010-2016 Akretion (www.akretion.com)
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, _
from openerp.exceptions import UserError
from lxml import etree


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    @api.multi
    def generate_payment_file(self):
        """Creates the SEPA Credit Transfer file. That's the important code!"""
        self.ensure_one()
        if (
                self.payment_mode_id.payment_method_id.code !=
                'sepa_credit_transfer'):
            return super(AccountPaymentOrder, self).generate_payment_file()

        pain_flavor = self.payment_mode_id.payment_method_id.pain_version
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
        pay_method = self.payment_mode_id.payment_method_id
        xsd_file = pay_method.get_xsd_file_path()
        gen_args = {
            'bic_xml_tag': bic_xml_tag,
            'name_maxsize': name_maxsize,
            'convert_to_ascii': pay_method.convert_to_ascii,
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
        group_header_1_0, nb_of_transactions_1_6, control_sum_1_7 = \
            self.generate_group_header_block(pain_root, gen_args)
        transactions_count_1_6 = 0
        amount_control_sum_1_7 = 0.0
        lines_per_group = {}
        # key = (requested_date, priority, local_instrument)
        # values = list of lines as object
        for line in self.bank_line_ids:
            priority = line.priority
            local_instrument = line.local_instrument
            # The field line.date is the requested payment date
            # taking into account the 'date_prefered' setting
            # cf account_banking_payment_export/models/account_payment.py
            # in the inherit of action_open()
            key = (line.date, priority, local_instrument)
            if key in lines_per_group:
                lines_per_group[key].append(line)
            else:
                lines_per_group[key] = [line]
        for (requested_date, priority, local_instrument), lines in\
                lines_per_group.items():
            # B. Payment info
            payment_info_2_0, nb_of_transactions_2_4, control_sum_2_5 = \
                self.generate_start_payment_info_block(
                    pain_root,
                    "self.name + '-' "
                    "+ requested_date.replace('-', '')  + '-' + priority + "
                    "'-' + local_instrument",
                    priority, local_instrument, False, requested_date, {
                        'self': self,
                        'priority': priority,
                        'requested_date': requested_date,
                        'local_instrument': local_instrument or 'NOinstr',
                    }, gen_args)
            self.generate_party_block(
                payment_info_2_0, 'Dbtr', 'B',
                self.company_partner_bank_id, gen_args)
            charge_bearer_2_24 = etree.SubElement(payment_info_2_0, 'ChrgBr')
            if self.sepa:
                charge_bearer = 'SLEV'
            else:
                charge_bearer = self.charge_bearer
            charge_bearer_2_24.text = charge_bearer
            transactions_count_2_4 = 0
            amount_control_sum_2_5 = 0.0
            for line in lines:
                transactions_count_1_6 += 1
                transactions_count_2_4 += 1
                # C. Credit Transfer Transaction Info
                credit_transfer_transaction_info_2_27 = etree.SubElement(
                    payment_info_2_0, 'CdtTrfTxInf')
                payment_identification_2_28 = etree.SubElement(
                    credit_transfer_transaction_info_2_27, 'PmtId')
                end2end_identification_2_30 = etree.SubElement(
                    payment_identification_2_28, 'EndToEndId')
                end2end_identification_2_30.text = self._prepare_field(
                    'End to End Identification', 'line.name',
                    {'line': line}, 35, gen_args=gen_args)
                currency_name = self._prepare_field(
                    'Currency Code', 'line.currency_id.name',
                    {'line': line}, 3, gen_args=gen_args)
                amount_2_42 = etree.SubElement(
                    credit_transfer_transaction_info_2_27, 'Amt')
                instructed_amount_2_43 = etree.SubElement(
                    amount_2_42, 'InstdAmt', Ccy=currency_name)
                instructed_amount_2_43.text = '%.2f' % line.amount_currency
                amount_control_sum_1_7 += line.amount_currency
                amount_control_sum_2_5 += line.amount_currency
                if not line.partner_bank_id:
                    raise UserError(
                        _("Bank account is missing on the bank payment line "
                            "of partner '%s' (reference '%s').")
                        % (line.partner_id.name, line.name))
                self.generate_party_block(
                    credit_transfer_transaction_info_2_27, 'Cdtr',
                    'C', line.partner_bank_id, gen_args, line)
                self.generate_remittance_info_block(
                    credit_transfer_transaction_info_2_27, line, gen_args)
            if not pain_flavor.startswith('pain.001.001.02'):
                nb_of_transactions_2_4.text = unicode(transactions_count_2_4)
                control_sum_2_5.text = '%.2f' % amount_control_sum_2_5
        if not pain_flavor.startswith('pain.001.001.02'):
            nb_of_transactions_1_6.text = unicode(transactions_count_1_6)
            control_sum_1_7.text = '%.2f' % amount_control_sum_1_7
        else:
            nb_of_transactions_1_6.text = unicode(transactions_count_1_6)
            control_sum_1_7.text = '%.2f' % amount_control_sum_1_7
        return self.finalize_sepa_file_creation(xml_root, gen_args)
