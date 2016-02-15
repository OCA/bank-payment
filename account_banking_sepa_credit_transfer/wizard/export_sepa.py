# -*- coding: utf-8 -*-
# © 2010-2015 Akretion (www.akretion.com)
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from openerp import workflow
from lxml import etree


class BankingExportSepaWizard(models.TransientModel):
    _name = 'banking.export.sepa.wizard'
    _inherit = ['banking.export.pain']
    _description = 'Export SEPA Credit Transfer File'

    state = fields.Selection([
        ('create', 'Create'),
        ('finish', 'Finish')],
        string='State', readonly=True, default='create')
    batch_booking = fields.Boolean(
        string='Batch Booking',
        help="If true, the bank statement will display only one debit "
        "line for all the wire transfers of the SEPA XML file ; if "
        "false, the bank statement will display one debit line per wire "
        "transfer of the SEPA XML file.")
    charge_bearer = fields.Selection([
        ('SLEV', 'Following Service Level'),
        ('SHAR', 'Shared'),
        ('CRED', 'Borne by Creditor'),
        ('DEBT', 'Borne by Debtor')], string='Charge Bearer',
        default='SLEV', required=True,
        help="Following service level : transaction charges are to be "
        "applied following the rules agreed in the service level "
        "and/or scheme (SEPA Core messages must use this). Shared : "
        "transaction charges on the debtor side are to be borne by "
        "the debtor, transaction charges on the creditor side are to "
        "be borne by the creditor. Borne by creditor : all "
        "transaction charges are to be borne by the creditor. Borne "
        "by debtor : all transaction charges are to be borne by the "
        "debtor.")
    nb_transactions = fields.Integer(
        string='Number of Transactions', readonly=True)
    total_amount = fields.Float(string='Total Amount', readonly=True)
    file = fields.Binary(string="File", readonly=True)
    filename = fields.Char(string="Filename", readonly=True)
    payment_order_ids = fields.Many2many(
        'payment.order', 'wiz_sepa_payorders_rel', 'wizard_id',
        'payment_order_id', string='Payment Orders', readonly=True)

    @api.model
    def create(self, vals):
        payment_order_ids = self._context.get('active_ids', [])
        vals.update({
            'payment_order_ids': [[6, 0, payment_order_ids]],
        })
        return super(BankingExportSepaWizard, self).create(vals)

    @api.multi
    def create_sepa(self):
        """Creates the SEPA Credit Transfer file. That's the important code!"""
        pain_flavor = self.payment_order_ids[0].mode.type.code
        convert_to_ascii = \
            self.payment_order_ids[0].mode.convert_to_ascii
        if pain_flavor == 'pain.001.001.02':
            bic_xml_tag = 'BIC'
            name_maxsize = 70
            root_xml_tag = 'pain.001.001.02'
        elif pain_flavor == 'pain.001.001.03':
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
        elif pain_flavor == 'pain.001.001.04':
            bic_xml_tag = 'BICFI'
            name_maxsize = 140
            root_xml_tag = 'CstmrCdtTrfInitn'
        elif pain_flavor == 'pain.001.001.05':
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
            raise Warning(
                _("Payment Type Code '%s' is not supported. The only "
                  "Payment Type Codes supported for SEPA Credit Transfers "
                  "are 'pain.001.001.02', 'pain.001.001.03', "
                  "'pain.001.001.04', 'pain.001.001.05'"
                  " and 'pain.001.003.03'.") %
                pain_flavor)
        gen_args = {
            'bic_xml_tag': bic_xml_tag,
            'name_maxsize': name_maxsize,
            'convert_to_ascii': convert_to_ascii,
            'payment_method': 'TRF',
            'file_prefix': 'sct_',
            'pain_flavor': pain_flavor,
            'pain_xsd_file':
            'account_banking_sepa_credit_transfer/data/%s.xsd'
            % pain_flavor,
        }
        pain_ns = {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            None: 'urn:iso:std:iso:20022:tech:xsd:%s' % pain_flavor,
        }
        xml_root = etree.Element('Document', nsmap=pain_ns)
        pain_root = etree.SubElement(xml_root, root_xml_tag)
        pain_03_to_05 = [
            'pain.001.001.03',
            'pain.001.001.04',
            'pain.001.001.05',
            'pain.001.003.03'
        ]
        # A. Group header
        group_header_1_0, nb_of_transactions_1_6, control_sum_1_7 = \
            self.generate_group_header_block(pain_root, gen_args)
        transactions_count_1_6 = 0
        total_amount = 0.0
        amount_control_sum_1_7 = 0.0
        lines_per_group = {}
        # key = (requested_date, priority)
        # values = list of lines as object
        for payment_order in self.payment_order_ids:
            total_amount = total_amount + payment_order.total
            for line in payment_order.bank_line_ids:
                priority = line.priority
                # The field line.date is the requested payment date
                # taking into account the 'date_prefered' setting
                # cf account_banking_payment_export/models/account_payment.py
                # in the inherit of action_open()
                key = (line.date, priority)
                if key in lines_per_group:
                    lines_per_group[key].append(line)
                else:
                    lines_per_group[key] = [line]
        for (requested_date, priority), lines in lines_per_group.items():
            # B. Payment info
            payment_info_2_0, nb_of_transactions_2_4, control_sum_2_5 = \
                self.generate_start_payment_info_block(
                    pain_root,
                    "self.payment_order_ids[0].reference + '-' "
                    "+ requested_date.replace('-', '')  + '-' + priority",
                    priority, False, False, requested_date, {
                        'self': self,
                        'priority': priority,
                        'requested_date': requested_date,
                    }, gen_args)
            self.generate_party_block(
                payment_info_2_0, 'Dbtr', 'B',
                'self.payment_order_ids[0].mode.bank_id.partner_id.'
                'name',
                'self.payment_order_ids[0].mode.bank_id.acc_number',
                'self.payment_order_ids[0].mode.bank_id.bank.bic or '
                'self.payment_order_ids[0].mode.bank_id.bank_bic',
                {'self': self},
                gen_args)
            charge_bearer_2_24 = etree.SubElement(payment_info_2_0, 'ChrgBr')
            charge_bearer_2_24.text = self.charge_bearer
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
                    'Currency Code', 'line.currency.name',
                    {'line': line}, 3, gen_args=gen_args)
                amount_2_42 = etree.SubElement(
                    credit_transfer_transaction_info_2_27, 'Amt')
                instructed_amount_2_43 = etree.SubElement(
                    amount_2_42, 'InstdAmt', Ccy=currency_name)
                instructed_amount_2_43.text = '%.2f' % line.amount_currency
                amount_control_sum_1_7 += line.amount_currency
                amount_control_sum_2_5 += line.amount_currency
                if not line.bank_id:
                    raise Warning(
                        _("Bank account is missing on the bank payment line "
                            "of partner '%s' (reference '%s').")
                        % (line.partner_id.name, line.name))
                self.generate_party_block(
                    credit_transfer_transaction_info_2_27, 'Cdtr',
                    'C', 'line.partner_id.name', 'line.bank_id.acc_number',
                    'line.bank_id.bank.bic or '
                    'line.bank_id.bank_bic', {'line': line}, gen_args)
                self.generate_remittance_info_block(
                    credit_transfer_transaction_info_2_27, line, gen_args)
            if pain_flavor in pain_03_to_05:
                nb_of_transactions_2_4.text = unicode(transactions_count_2_4)
                control_sum_2_5.text = '%.2f' % amount_control_sum_2_5
        if pain_flavor in pain_03_to_05:
            nb_of_transactions_1_6.text = unicode(transactions_count_1_6)
            control_sum_1_7.text = '%.2f' % amount_control_sum_1_7
        else:
            nb_of_transactions_1_6.text = unicode(transactions_count_1_6)
            control_sum_1_7.text = '%.2f' % amount_control_sum_1_7
        return self.finalize_sepa_file_creation(
            xml_root, total_amount, transactions_count_1_6, gen_args)

    @api.multi
    def save_sepa(self):
        """Save the SEPA file: send the done signal to all payment
        orders in the file. With the default workflow, they will
        transition to 'done', while with the advanced workflow in
        account_banking_payment they will transition to 'sent' waiting
        reconciliation.
        """
        for order in self.payment_order_ids:
            workflow.trg_validate(
                self._uid, 'payment.order', order.id, 'done', self._cr)
            self.env['ir.attachment'].create({
                'res_model': 'payment.order',
                'res_id': order.id,
                'name': self.filename,
                'datas': self.file,
                })
        return True
