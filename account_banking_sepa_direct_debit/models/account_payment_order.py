# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import UserError
from lxml import etree


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    @api.multi
    def generate_payment_file(self):
        """Creates the SEPA Direct Debit file. That's the important code !"""
        self.ensure_one()
        if self.payment_method_id.code != 'sepa_direct_debit':
            return super(AccountPaymentOrder, self).generate_payment_file()
        pain_flavor = self.payment_method_id.pain_version
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
        group_header, nb_of_transactions_a, control_sum_a = \
            self.generate_group_header_block(pain_root, gen_args)
        transactions_count_a = 0
        amount_control_sum_a = 0.0
        lines_per_group = {}
        # key = (requested_date, priority, sequence type)
        # value = list of lines as objects
        for line in self.bank_line_ids:
            transactions_count_a += 1
            priority = line.priority
            categ_purpose = line.category_purpose
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
            key = (line.date, priority, categ_purpose, seq_type, scheme)
            if key in lines_per_group:
                lines_per_group[key].append(line)
            else:
                lines_per_group[key] = [line]

        for (requested_date, priority, categ_purpose, sequence_type, scheme),\
                lines in lines_per_group.items():
            # B. Payment info
            payment_info, nb_of_transactions_b, control_sum_b = \
                self.generate_start_payment_info_block(
                    pain_root,
                    "self.name + '-' + "
                    "sequence_type + '-' + requested_date.replace('-', '')  "
                    "+ '-' + priority + '-' + category_purpose",
                    priority, scheme, categ_purpose,
                    sequence_type, requested_date, {
                        'self': self,
                        'sequence_type': sequence_type,
                        'priority': priority,
                        'category_purpose': categ_purpose or 'NOcateg',
                        'requested_date': requested_date,
                    }, gen_args)

            self.generate_party_block(
                payment_info, 'Cdtr', 'B',
                self.company_partner_bank_id, gen_args)
            charge_bearer = etree.SubElement(payment_info, 'ChrgBr')
            if self.sepa:
                charge_bearer_text = 'SLEV'
            else:
                charge_bearer_text = self.charge_bearer
            charge_bearer.text = charge_bearer_text
            creditor_scheme_identification = etree.SubElement(
                payment_info, 'CdtrSchmeId')
            self.generate_creditor_scheme_identification(
                creditor_scheme_identification,
                'self.payment_mode_id.sepa_creditor_identifier or '
                'self.company_id.sepa_creditor_identifier',
                'SEPA Creditor Identifier', {'self': self}, 'SEPA', gen_args)
            transactions_count_b = 0
            amount_control_sum_b = 0.0
            for line in lines:
                transactions_count_b += 1
                # C. Direct Debit Transaction Info
                dd_transaction_info = etree.SubElement(
                    payment_info, 'DrctDbtTxInf')
                payment_identification = etree.SubElement(
                    dd_transaction_info, 'PmtId')
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
                instructed_amount = etree.SubElement(
                    dd_transaction_info, 'InstdAmt', Ccy=currency_name)
                instructed_amount.text = '%.2f' % line.amount_currency
                amount_control_sum_a += line.amount_currency
                amount_control_sum_b += line.amount_currency
                dd_transaction = etree.SubElement(
                    dd_transaction_info, 'DrctDbtTx')
                mandate_related_info = etree.SubElement(
                    dd_transaction, 'MndtRltdInf')
                mandate_identification = etree.SubElement(
                    mandate_related_info, 'MndtId')
                mandate_identification.text = self._prepare_field(
                    'Unique Mandate Reference',
                    'line.mandate_id.unique_mandate_reference',
                    {'line': line}, 35, gen_args=gen_args)
                mandate_signature_date = etree.SubElement(
                    mandate_related_info, 'DtOfSgntr')
                mandate_signature_date.text = self._prepare_field(
                    'Mandate Signature Date',
                    'line.mandate_id.signature_date',
                    {'line': line}, 10, gen_args=gen_args)
                if sequence_type == 'FRST' and line.mandate_id.last_debit_date:
                    amendment_indicator = etree.SubElement(
                        mandate_related_info, 'AmdmntInd')
                    amendment_indicator.text = 'true'
                    amendment_info_details = etree.SubElement(
                        mandate_related_info, 'AmdmntInfDtls')
                    ori_debtor_account = etree.SubElement(
                        amendment_info_details, 'OrgnlDbtrAcct')
                    ori_debtor_account_id = etree.SubElement(
                        ori_debtor_account, 'Id')
                    ori_debtor_agent_other = etree.SubElement(
                        ori_debtor_account_id, 'Othr')
                    ori_debtor_agent_other_id = etree.SubElement(
                        ori_debtor_agent_other, 'Id')
                    ori_debtor_agent_other_id.text = 'SMNDA'
                    # Until 20/11/2016, SMNDA meant
                    # "Same Mandate New Debtor Agent"
                    # After 20/11/2016, SMNDA means
                    # "Same Mandate New Debtor Account"

                self.generate_party_block(
                    dd_transaction_info, 'Dbtr', 'C',
                    line.partner_bank_id, gen_args, line)

                if line.purpose:
                    purpose = etree.SubElement(
                        dd_transaction_info, 'Purp')
                    etree.SubElement(purpose, 'Cd').text = line.purpose

                self.generate_remittance_info_block(
                    dd_transaction_info, line, gen_args)

            nb_of_transactions_b.text = unicode(transactions_count_b)
            control_sum_b.text = '%.2f' % amount_control_sum_b
        nb_of_transactions_a.text = unicode(transactions_count_a)
        control_sum_a.text = '%.2f' % amount_control_sum_a

        return self.finalize_sepa_file_creation(
            xml_root, gen_args)

    @api.multi
    def generated2uploaded(self):
        """Write 'last debit date' on mandates
        Set mandates from first to recurring
        Set oneoff mandates to expired
        """
        # I call super() BEFORE updating the sequence_type
        # from first to recurring, so that the account move
        # is generated BEFORE, which will allow the split
        # of the account move per sequence_type
        res = super(AccountPaymentOrder, self).generated2uploaded()
        abmo = self.env['account.banking.mandate']
        for order in self:
            to_expire_mandates = abmo.browse([])
            first_mandates = abmo.browse([])
            all_mandates = abmo.browse([])
            for bline in order.bank_line_ids:
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
                {'last_debit_date': order.date_generated})
            to_expire_mandates.write({'state': 'expired'})
            first_mandates.write({
                'recurrent_sequence_type': 'recurring',
                })
            for first_mandate in first_mandates:
                first_mandate.message_post(_(
                    "Automatically switched from <b>First</b> to "
                    "<b>Recurring</b> when the debit order "
                    "<a href=# data-oe-model=account.payment.order "
                    "data-oe-id=%d>%s</a> has been marked as uploaded.")
                    % (order.id, order.name))
        return res
