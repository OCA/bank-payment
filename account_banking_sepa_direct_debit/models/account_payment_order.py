# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import UserError
from lxml import etree


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    def _get_previous_bank(self, payline):
        previous_bank = False
        older_lines = self.env['account.payment.line'].search([
            ('mandate_id', '=', payline.mandate_id.id),
            ('partner_bank_id', '!=', payline.partner_bank_id.id)])
        if older_lines:
            previous_date = False
            previous_payline = False
            for older_line in older_lines:
                if hasattr(older_line.order_id, 'date_sent'):
                    older_line_date = older_line.order_id.date_sent
                else:
                    older_line_date = older_line.order_id.date_done
                if (older_line_date and
                        older_line_date > previous_date):
                    previous_date = older_line_date
                    previous_payline = older_line
            if previous_payline:
                previous_bank = previous_payline.partner_bank_id
        return previous_bank

    @api.multi
    def generate_payment_file(self):
        """Creates the SEPA Direct Debit file. That's the important code !"""
        self.ensure_one()
        if (
                self.payment_mode_id.payment_method_id.code !=
                'sepa_direct_debit'):
            return super(AccountPaymentOrder, self).generate_payment_file()
        pain_flavor = self.payment_mode_id.payment_method_id.pain_version
        # We use pain_flavor.startswith('pain.008.001.xx')
        # to support country-specific extensions such as
        # pain.008.001.02.ch.01 (cf l10n_ch_sepa)
        if pain_flavor.startswith('pain.008.001.02'):
            bic_xml_tag = 'BIC'
            name_maxsize = 70
            root_xml_tag = 'CstmrDrctDbtInitn'
        elif pain_flavor.startswith('pain.008.003.02'):
            bic_xml_tag = 'BIC'
            name_maxsize = 70
            root_xml_tag = 'CstmrDrctDbtInitn'
        elif pain_flavor.startswith('pain.008.001.03'):
            bic_xml_tag = 'BICFI'
            name_maxsize = 140
            root_xml_tag = 'CstmrDrctDbtInitn'
        elif pain_flavor.startswith('pain.008.001.04'):
            bic_xml_tag = 'BICFI'
            name_maxsize = 140
            root_xml_tag = 'CstmrDrctDbtInitn'
        else:
            raise UserError(
                _("Payment Type Code '%s' is not supported. The only "
                  "Payment Type Code supported for SEPA Direct Debit are "
                  "'pain.008.001.02', 'pain.008.001.03' and "
                  "'pain.008.001.04'.") % pain_flavor)
        pay_method = self.payment_mode_id.payment_method_id
        xsd_file = pay_method.get_xsd_file_path()
        gen_args = {
            'bic_xml_tag': bic_xml_tag,
            'name_maxsize': name_maxsize,
            'convert_to_ascii': pay_method.convert_to_ascii,
            'payment_method': 'DD',
            'file_prefix': 'sdd_',
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
        # key = (requested_date, priority, sequence type)
        # value = list of lines as objects
        for line in self.bank_line_ids:
            transactions_count_1_6 += 1
            priority = line.priority
            # The field line.date is the requested payment date
            # taking into account the 'date_prefered' setting
            # cf account_banking_payment_export/models/account_payment.py
            # in the inherit of action_open()
            if not line.mandate_id:
                raise UserError(
                    _("Missing SEPA Direct Debit mandate on the "
                      "bank payment line with partner '%s' "
                      "(reference '%s').")
                    % (line.partner_id.name, line.name))
            scheme = line.mandate_id.scheme
            if line.mandate_id.state != 'valid':
                raise Warning(
                    _("The SEPA Direct Debit mandate with reference '%s' "
                      "for partner '%s' has expired.")
                    % (line.mandate_id.unique_mandate_reference,
                       line.mandate_id.partner_id.name))
            if line.mandate_id.type == 'oneoff':
                seq_type = 'OOFF'
                if line.mandate_id.last_debit_date:
                    raise Warning(
                        _("The mandate with reference '%s' for partner "
                          "'%s' has type set to 'One-Off' and it has a "
                          "last debit date set to '%s', so we can't use "
                          "it.")
                        % (line.mandate_id.unique_mandate_reference,
                           line.mandate_id.partner_id.name,
                           line.mandate_id.last_debit_date))
            elif line.mandate_id.type == 'recurrent':
                seq_type_map = {
                    'recurring': 'RCUR',
                    'first': 'FRST',
                    'final': 'FNAL',
                }
                seq_type_label = \
                    line.mandate_id.recurrent_sequence_type
                assert seq_type_label is not False
                seq_type = seq_type_map[seq_type_label]
            key = (line.date, priority, seq_type, scheme)
            if key in lines_per_group:
                lines_per_group[key].append(line)
            else:
                lines_per_group[key] = [line]

        for (requested_date, priority, sequence_type, scheme), lines in \
                lines_per_group.items():
            # B. Payment info
            payment_info_2_0, nb_of_transactions_2_4, control_sum_2_5 = \
                self.generate_start_payment_info_block(
                    pain_root,
                    "self.name + '-' + "
                    "sequence_type + '-' + requested_date.replace('-', '')  "
                    "+ '-' + priority",
                    priority, scheme, sequence_type, requested_date, {
                        'self': self,
                        'sequence_type': sequence_type,
                        'priority': priority,
                        'requested_date': requested_date,
                    }, gen_args)

            self.generate_party_block(
                payment_info_2_0, 'Cdtr', 'B',
                self.company_partner_bank_id, gen_args)
            charge_bearer_2_24 = etree.SubElement(payment_info_2_0, 'ChrgBr')
            if self.sepa:
                charge_bearer = 'SLEV'
            else:
                charge_bearer = self.charge_bearer
            charge_bearer_2_24.text = charge_bearer
            creditor_scheme_identification_2_27 = etree.SubElement(
                payment_info_2_0, 'CdtrSchmeId')
            self.generate_creditor_scheme_identification(
                creditor_scheme_identification_2_27,
                'self.payment_mode_id.sepa_creditor_identifier or '
                'self.company_id.sepa_creditor_identifier',
                'SEPA Creditor Identifier', {'self': self}, 'SEPA', gen_args)
            transactions_count_2_4 = 0
            amount_control_sum_2_5 = 0.0
            for line in lines:
                transactions_count_2_4 += 1
                # C. Direct Debit Transaction Info
                dd_transaction_info_2_28 = etree.SubElement(
                    payment_info_2_0, 'DrctDbtTxInf')
                payment_identification_2_29 = etree.SubElement(
                    dd_transaction_info_2_28, 'PmtId')
                if pain_flavor == 'pain.008.001.02.ch.01':
                    instruction_identification = etree.SubElement(
                        payment_identification_2_29, 'InstrId')
                    instruction_identification.text = self._prepare_field(
                        'Intruction Identification', 'line.name',
                        {'line': line}, 35, gen_args=gen_args)
                end2end_identification_2_31 = etree.SubElement(
                    payment_identification_2_29, 'EndToEndId')
                end2end_identification_2_31.text = self._prepare_field(
                    'End to End Identification', 'line.name',
                    {'line': line}, 35, gen_args=gen_args)
                currency_name = self._prepare_field(
                    'Currency Code', 'line.currency_id.name',
                    {'line': line}, 3, gen_args=gen_args)
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
                    'Unique Mandate Reference',
                    'line.mandate_id.unique_mandate_reference',
                    {'line': line}, 35, gen_args=gen_args)
                mandate_signature_date_2_49 = etree.SubElement(
                    mandate_related_info_2_47, 'DtOfSgntr')
                mandate_signature_date_2_49.text = self._prepare_field(
                    'Mandate Signature Date',
                    'line.mandate_id.signature_date',
                    {'line': line}, 10, gen_args=gen_args)
                if sequence_type == 'FRST' and line.mandate_id.last_debit_date:
                    previous_bank = self._get_previous_bank(line)
                    if previous_bank:
                        amendment_indicator_2_50 = etree.SubElement(
                            mandate_related_info_2_47, 'AmdmntInd')
                        amendment_indicator_2_50.text = 'true'
                        amendment_info_details_2_51 = etree.SubElement(
                            mandate_related_info_2_47, 'AmdmntInfDtls')
                        if (
                                previous_bank.bank_bic ==
                                line.partner_bank_id.bank_bic):
                            ori_debtor_account_2_57 = etree.SubElement(
                                amendment_info_details_2_51, 'OrgnlDbtrAcct')
                            ori_debtor_account_id = etree.SubElement(
                                ori_debtor_account_2_57, 'Id')
                            ori_debtor_account_iban = etree.SubElement(
                                ori_debtor_account_id, 'IBAN')
                            ori_debtor_account_iban.text = self._validate_iban(
                                self._prepare_field(
                                    'Original Debtor Account',
                                    'previous_bank.sanitized_acc_number',
                                    {'previous_bank': previous_bank},
                                    gen_args=gen_args))
                        else:
                            ori_debtor_agent_2_58 = etree.SubElement(
                                amendment_info_details_2_51, 'OrgnlDbtrAgt')
                            ori_debtor_agent_institution = etree.SubElement(
                                ori_debtor_agent_2_58, 'FinInstnId')
                            ori_debtor_agent_bic = etree.SubElement(
                                ori_debtor_agent_institution, bic_xml_tag)
                            ori_debtor_agent_bic.text = self._prepare_field(
                                'Original Debtor Agent',
                                'previous_bank.bank_bic',
                                {'previous_bank': previous_bank},
                                gen_args=gen_args)
                            ori_debtor_agent_other = etree.SubElement(
                                ori_debtor_agent_institution, 'Othr')
                            ori_debtor_agent_other_id = etree.SubElement(
                                ori_debtor_agent_other, 'Id')
                            ori_debtor_agent_other_id.text = 'SMNDA'
                            # SMNDA = Same Mandate New Debtor Agent

                self.generate_party_block(
                    dd_transaction_info_2_28, 'Dbtr', 'C',
                    line.partner_bank_id, gen_args, line)

                self.generate_remittance_info_block(
                    dd_transaction_info_2_28, line, gen_args)

            nb_of_transactions_2_4.text = unicode(transactions_count_2_4)
            control_sum_2_5.text = '%.2f' % amount_control_sum_2_5
        nb_of_transactions_1_6.text = unicode(transactions_count_1_6)
        control_sum_1_7.text = '%.2f' % amount_control_sum_1_7

        return self.finalize_sepa_file_creation(
            xml_root, gen_args)

    @api.multi
    def finalize_sepa_file_creation(self, xml_root, gen_args):
        """Save the SEPA Direct Debit file: mark all payments in the file
        as 'sent'. Write 'last debit date' on mandate and set oneoff
        mandate to expired.
        """
        abmo = self.env['account.banking.mandate']
        to_expire_mandates = abmo.browse([])
        first_mandates = abmo.browse([])
        all_mandates = abmo.browse([])
        for bline in self.bank_line_ids:
            if bline.mandate_id in all_mandates:
                continue
            all_mandates += bline.mandate_id
            if bline.mandate_id.type == 'oneoff':
                to_expire_mandates += bline.mandate_id
            elif bline.mandate_id.type == 'recurrent':
                seq_type = bline.mandate_id.recurrent_sequence_type
                if seq_type == 'final':
                    to_expire_mandates += bline.mandate_id
                elif seq_type == 'first':
                    first_mandates += bline.mandate_id
        all_mandates.write(
            {'last_debit_date': fields.Date.context_today(self)})
        to_expire_mandates.write({'state': 'expired'})
        first_mandates.write({
            'recurrent_sequence_type': 'recurring',
            })
        return super(AccountPaymentOrder, self).finalize_sepa_file_creation(
            xml_root, gen_args)
