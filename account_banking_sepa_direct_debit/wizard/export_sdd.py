# -*- encoding: utf-8 -*-
##############################################################################
#
#    SEPA Direct Debit module for Odoo
#    Copyright (C) 2013-2015 Akretion (http://www.akretion.com)
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


from openerp import models, fields, api, _
from openerp.exceptions import Warning
from openerp import workflow
from lxml import etree


class BankingExportSddWizard(models.TransientModel):
    _name = 'banking.export.sdd.wizard'
    _inherit = ['banking.export.pain']
    _description = 'Export SEPA Direct Debit File'

    state = fields.Selection([
        ('create', 'Create'),
        ('finish', 'Finish'),
        ], string='State', readonly=True, default='create')
    batch_booking = fields.Boolean(
        string='Batch Booking',
        help="If true, the bank statement will display only one credit "
        "line for all the direct debits of the SEPA file ; if false, "
        "the bank statement will display one credit line per direct "
        "debit of the SEPA file.")
    charge_bearer = fields.Selection([
        ('SLEV', 'Following Service Level'),
        ('SHAR', 'Shared'),
        ('CRED', 'Borne by Creditor'),
        ('DEBT', 'Borne by Debtor'),
        ], string='Charge Bearer', required=True, default='SLEV',
        help="Following service level : transaction charges are to be "
        "applied following the rules agreed in the service level "
        "and/or scheme (SEPA Core messages must use this). Shared : "
        "transaction charges on the creditor side are to be borne "
        "by the creditor, transaction charges on the debtor side are "
        "to be borne by the debtor. Borne by creditor : all "
        "transaction charges are to be borne by the creditor. Borne "
        "by debtor : all transaction charges are to be borne by the debtor.")
    nb_transactions = fields.Integer(
        string='Number of Transactions', readonly=True)
    total_amount = fields.Float(string='Total Amount', readonly=True)
    file = fields.Binary(string="File", readonly=True)
    filename = fields.Char(string="Filename", readonly=True)
    payment_order_ids = fields.Many2many(
        'payment.order', 'wiz_sdd_payorders_rel', 'wizard_id',
        'payment_order_id', string='Payment Orders', readonly=True)

    @api.model
    def create(self, vals):
        payment_order_ids = self._context.get('active_ids', [])
        vals.update({
            'payment_order_ids': [[6, 0, payment_order_ids]],
        })
        return super(BankingExportSddWizard, self).create(vals)

    def _get_previous_bank(self, payline):
        previous_bank = False
        older_lines = self.env['payment.line'].search([
            ('mandate_id', '=', payline.mandate_id.id),
            ('bank_id', '!=', payline.bank_id.id)])
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
                previous_bank = previous_payline.bank_id
        return previous_bank

    @api.multi
    def create_sepa(self):
        """Creates the SEPA Direct Debit file. That's the important code !"""
        pain_flavor = self.payment_order_ids[0].mode.type.code
        convert_to_ascii = \
            self.payment_order_ids[0].mode.convert_to_ascii
        if pain_flavor == 'pain.008.001.02':
            bic_xml_tag = 'BIC'
            name_maxsize = 70
            root_xml_tag = 'CstmrDrctDbtInitn'
        elif pain_flavor == 'pain.008.001.03':
            bic_xml_tag = 'BICFI'
            name_maxsize = 140
            root_xml_tag = 'CstmrDrctDbtInitn'
        elif pain_flavor == 'pain.008.001.04':
            bic_xml_tag = 'BICFI'
            name_maxsize = 140
            root_xml_tag = 'CstmrDrctDbtInitn'
        else:
            raise Warning(
                _("Payment Type Code '%s' is not supported. The only "
                  "Payment Type Code supported for SEPA Direct Debit are "
                  "'pain.008.001.02', 'pain.008.001.03' and "
                  "'pain.008.001.04'.") % pain_flavor)
        gen_args = {
            'bic_xml_tag': bic_xml_tag,
            'name_maxsize': name_maxsize,
            'convert_to_ascii': convert_to_ascii,
            'payment_method': 'DD',
            'file_prefix': 'sdd_',
            'pain_flavor': pain_flavor,
            'pain_xsd_file':
            'account_banking_sepa_direct_debit/data/%s.xsd' % pain_flavor,
        }
        pain_ns = {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            None: 'urn:iso:std:iso:20022:tech:xsd:%s' % pain_flavor,
        }
        xml_root = etree.Element('Document', nsmap=pain_ns)
        pain_root = etree.SubElement(xml_root, root_xml_tag)
        # A. Group header
        group_header_1_0, nb_of_transactions_1_6, control_sum_1_7 = \
            self.generate_group_header_block(pain_root, gen_args)
        transactions_count_1_6 = 0
        total_amount = 0.0
        amount_control_sum_1_7 = 0.0
        lines_per_group = {}
        # key = (requested_date, priority, sequence type)
        # value = list of lines as objects
        # Iterate on payment orders
        for payment_order in self.payment_order_ids:
            total_amount = total_amount + payment_order.total
            # Iterate each payment lines
            for line in payment_order.bank_line_ids:
                transactions_count_1_6 += 1
                priority = line.priority
                # The field line.date is the requested payment date
                # taking into account the 'date_prefered' setting
                # cf account_banking_payment_export/models/account_payment.py
                # in the inherit of action_open()
                if not line.mandate_id:
                    raise Warning(
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
                    "self.payment_order_ids[0].reference + '-' + "
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
                'self.payment_order_ids[0].mode.bank_id.partner_id.'
                'name',
                'self.payment_order_ids[0].mode.bank_id.acc_number',
                'self.payment_order_ids[0].mode.bank_id.bank.bic or '
                'self.payment_order_ids[0].mode.bank_id.bank_bic',
                {'self': self}, gen_args)
            charge_bearer_2_24 = etree.SubElement(payment_info_2_0, 'ChrgBr')
            charge_bearer_2_24.text = self.charge_bearer
            creditor_scheme_identification_2_27 = etree.SubElement(
                payment_info_2_0, 'CdtrSchmeId')
            self.generate_creditor_scheme_identification(
                creditor_scheme_identification_2_27,
                'self.payment_order_ids[0].mode.'
                'sepa_creditor_identifier or '
                'self.payment_order_ids[0].company_id.'
                'sepa_creditor_identifier',
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
                end2end_identification_2_31 = etree.SubElement(
                    payment_identification_2_29, 'EndToEndId')
                end2end_identification_2_31.text = self._prepare_field(
                    'End to End Identification', 'line.name',
                    {'line': line}, 35, gen_args=gen_args)
                currency_name = self._prepare_field(
                    'Currency Code', 'line.currency.name',
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
                    amendment_indicator_2_50 = etree.SubElement(
                        mandate_related_info_2_47, 'AmdmntInd')
                    amendment_indicator_2_50.text = 'true'
                    amendment_info_details_2_51 = etree.SubElement(
                        mandate_related_info_2_47, 'AmdmntInfDtls')
                    ori_debtor_account_2_57 = etree.SubElement(
                        amendment_info_details_2_51, 'OrgnlDbtrAcct')
                    ori_debtor_account_id = etree.SubElement(
                        ori_debtor_account_2_57, 'Id')
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
                    dd_transaction_info_2_28, 'Dbtr', 'C',
                    'line.partner_id.name',
                    'line.bank_id.acc_number',
                    'line.bank_id.bank.bic or '
                    'line.bank_id.bank_bic',
                    {'line': line}, gen_args)

                self.generate_remittance_info_block(
                    dd_transaction_info_2_28, line, gen_args)

            nb_of_transactions_2_4.text = unicode(transactions_count_2_4)
            control_sum_2_5.text = '%.2f' % amount_control_sum_2_5
        nb_of_transactions_1_6.text = unicode(transactions_count_1_6)
        control_sum_1_7.text = '%.2f' % amount_control_sum_1_7

        return self.finalize_sepa_file_creation(
            xml_root, total_amount, transactions_count_1_6, gen_args)

    @api.multi
    def save_sepa(self):
        """Save the SEPA Direct Debit file: mark all payments in the file
        as 'sent'. Write 'last debit date' on mandate and set oneoff
        mandate to expired.
        """
        abmo = self.env['account.banking.mandate']
        for order in self.payment_order_ids:
            workflow.trg_validate(
                self._uid, 'payment.order', order.id, 'done', self._cr)
            self.env['ir.attachment'].create({
                'res_model': 'payment.order',
                'res_id': order.id,
                'name': self.filename,
                'datas': self.file,
                })
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
                {'last_debit_date': fields.Date.context_today(self)})
            to_expire_mandates.write({'state': 'expired'})
            first_mandates.write({
                'recurrent_sequence_type': 'recurring',
                })
        return True
