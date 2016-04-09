# -*- encoding: utf-8 -*-
##############################################################################
#
#    SEPA Direct Debit module for OpenERP
#    Copyright (C) 2013 Akretion (http://www.akretion.com)
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


from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp import netsvc
from datetime import datetime
from lxml import etree


class banking_export_sdd_wizard(orm.TransientModel):
    _name = 'banking.export.sdd.wizard'
    _inherit = ['banking.export.pain']
    _description = 'Export SEPA Direct Debit File'
    _columns = {
        'state': fields.selection([
            ('create', 'Create'),
            ('finish', 'Finish'),
        ], 'State', readonly=True),
        'batch_booking': fields.boolean(
            'Batch Booking',
            help="If true, the bank statement will display only one credit "
            "line for all the direct debits of the SEPA file ; if false, "
            "the bank statement will display one credit line per direct "
            "debit of the SEPA file."),
        'charge_bearer': fields.selection([
            ('SLEV', 'Following Service Level'),
            ('SHAR', 'Shared'),
            ('CRED', 'Borne by Creditor'),
            ('DEBT', 'Borne by Debtor'),
        ], 'Charge Bearer', required=True,
            help="Following service level : transaction charges are to be "
            "applied following the rules agreed in the service level and/or "
            "scheme (SEPA Core messages must use this). Shared : transaction "
            "charges on the creditor side are to be borne by the creditor, "
            "transaction charges on the debtor side are to be borne by the "
            "debtor. Borne by creditor : all transaction charges are to be "
            "borne by the creditor. Borne by debtor : all transaction "
            "charges are to be borne by the debtor."),
        'nb_transactions': fields.related(
            'file_id', 'nb_transactions', type='integer',
            string='Number of Transactions', readonly=True),
        'total_amount': fields.related(
            'file_id', 'total_amount', type='float', string='Total Amount',
            readonly=True),
        'file_id': fields.many2one(
            'banking.export.sdd', 'SDD File', readonly=True),
        'file': fields.related(
            'file_id', 'file', string="File", type='binary', readonly=True),
        'filename': fields.related(
            'file_id', 'filename', string="Filename", type='char', size=256,
            readonly=True),
        'payment_order_ids': fields.many2many(
            'payment.order', 'wiz_sdd_payorders_rel', 'wizard_id',
            'payment_order_id', 'Payment Orders', readonly=True),
    }

    _defaults = {
        'charge_bearer': 'SLEV',
        'state': 'create',
    }

    def create(self, cr, uid, vals, context=None):
        payment_order_ids = context.get('active_ids', [])
        vals.update({
            'payment_order_ids': [[6, 0, payment_order_ids]],
        })
        return super(banking_export_sdd_wizard, self).create(
            cr, uid, vals, context=context)

    def _get_previous_bank(self, cr, uid, payline, context=None):
        payline_obj = self.pool['payment.line']
        previous_bank = False
        payline_ids = payline_obj.search(
            cr, uid, [
                ('mandate_id', '=', payline.mandate_id.id),
                ('bank_id', '!=', payline.bank_id.id),
            ],
            context=context)
        if payline_ids:
            older_lines = payline_obj.browse(
                cr, uid, payline_ids, context=context)
            previous_date = False
            previous_payline_id = False
            for older_line in older_lines:
                older_line_date_sent = older_line.order_id.date_sent
                if (older_line_date_sent and
                        older_line_date_sent > previous_date):
                    previous_date = older_line_date_sent
                    previous_payline_id = older_line.id
            if previous_payline_id:
                previous_payline = payline_obj.browse(
                    cr, uid, previous_payline_id, context=context)
                previous_bank = previous_payline.bank_id
        return previous_bank

    def create_sepa(self, cr, uid, ids, context=None):
        '''
        Creates the SEPA Direct Debit file. That's the important code !
        '''
        sepa_export = self.browse(cr, uid, ids[0], context=context)

        pain_flavor = sepa_export.payment_order_ids[0].mode.type.code
        convert_to_ascii = \
            sepa_export.payment_order_ids[0].mode.convert_to_ascii
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
            raise orm.except_orm(
                _('Error:'),
                _("Payment Type Code '%s' is not supported. The only "
                    "Payment Type Code supported for SEPA Direct Debit "
                    "are 'pain.008.001.02', 'pain.008.001.03' and "
                    "'pain.008.001.04'.") % pain_flavor)

        gen_args = {
            'bic_xml_tag': bic_xml_tag,
            'name_maxsize': name_maxsize,
            'convert_to_ascii': convert_to_ascii,
            'payment_method': 'DD',
            'pain_flavor': pain_flavor,
            'sepa_export': sepa_export,
            'file_obj': self.pool['banking.export.sdd'],
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
            self.generate_group_header_block(
                cr, uid, pain_root, gen_args, context=context)

        transactions_count_1_6 = 0
        total_amount = 0.0
        amount_control_sum_1_7 = 0.0
        lines_per_group = {}
        # key = (requested_date, priority, sequence type)
        # value = list of lines as objects
        # Iterate on payment orders
        today = fields.date.context_today(self, cr, uid, context=context)
        for payment_order in sepa_export.payment_order_ids:
            total_amount = total_amount + payment_order.total
            # Iterate each payment lines
            for line in payment_order.line_ids:
                transactions_count_1_6 += 1
                priority = line.priority
                if payment_order.date_prefered == 'due':
                    requested_date = line.ml_maturity_date or today
                elif payment_order.date_prefered == 'fixed':
                    requested_date = payment_order.date_scheduled or today
                else:
                    requested_date = today
                if not line.mandate_id:
                    raise orm.except_orm(
                        _('Error:'),
                        _("Missing SEPA Direct Debit mandate on the payment "
                            "line with partner '%s' and Invoice ref '%s'.")
                        % (line.partner_id.name,
                            line.ml_inv_ref.number))
                scheme = line.mandate_id.scheme
                if line.mandate_id.state != 'valid':
                    raise orm.except_orm(
                        _('Error:'),
                        _("The SEPA Direct Debit mandate with reference '%s' "
                            "for partner '%s' has expired.")
                        % (line.mandate_id.unique_mandate_reference,
                            line.mandate_id.partner_id.name))
                if line.mandate_id.type == 'oneoff':
                    if not line.mandate_id.last_debit_date:
                        seq_type = 'OOFF'
                    else:
                        raise orm.except_orm(
                            _('Error:'),
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

                key = (requested_date, priority, seq_type, scheme)
                if key in lines_per_group:
                    lines_per_group[key].append(line)
                else:
                    lines_per_group[key] = [line]
                # Write requested_exec_date on 'Payment date' of the pay line
                if requested_date != line.date:
                    self.pool['payment.line'].write(
                        cr, uid, line.id,
                        {'date': requested_date}, context=context)

        for (requested_date, priority, sequence_type, scheme), lines in \
                lines_per_group.items():
            # B. Payment info
            payment_info_2_0, nb_of_transactions_2_4, control_sum_2_5 = \
                self.generate_start_payment_info_block(
                    cr, uid, pain_root,
                    "sepa_export.payment_order_ids[0].reference + '-' + "
                    "sequence_type + '-' + requested_date.replace('-', '')  "
                    "+ '-' + priority",
                    priority, scheme, sequence_type, requested_date, {
                        'sepa_export': sepa_export,
                        'sequence_type': sequence_type,
                        'priority': priority,
                        'requested_date': requested_date,
                    }, gen_args, context=context)

            self.generate_party_block(
                cr, uid, payment_info_2_0, 'Cdtr', 'B',
                'sepa_export.payment_order_ids[0].mode.bank_id.partner_id.'
                'name',
                'sepa_export.payment_order_ids[0].mode.bank_id.acc_number',
                'sepa_export.payment_order_ids[0].mode.bank_id.bank.bic',
                {'sepa_export': sepa_export},
                gen_args, context=context)

            charge_bearer_2_24 = etree.SubElement(payment_info_2_0, 'ChrgBr')
            charge_bearer_2_24.text = sepa_export.charge_bearer

            creditor_scheme_identification_2_27 = etree.SubElement(
                payment_info_2_0, 'CdtrSchmeId')
            self.generate_creditor_scheme_identification(
                cr, uid, creditor_scheme_identification_2_27,
                'sepa_export.payment_order_ids[0].company_id.'
                'sepa_creditor_identifier',
                'SEPA Creditor Identifier', {'sepa_export': sepa_export},
                'SEPA', gen_args, context=context)

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
                    cr, uid, 'End to End Identification', 'line.name',
                    {'line': line}, 35,
                    gen_args=gen_args, context=context)
                currency_name = self._prepare_field(
                    cr, uid, 'Currency Code', 'line.currency.name',
                    {'line': line}, 3, gen_args=gen_args,
                    context=context)
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
                    cr, uid, 'Unique Mandate Reference',
                    'line.mandate_id.unique_mandate_reference',
                    {'line': line}, 35,
                    gen_args=gen_args, context=context)
                mandate_signature_date_2_49 = etree.SubElement(
                    mandate_related_info_2_47, 'DtOfSgntr')
                mandate_signature_date_2_49.text = self._prepare_field(
                    cr, uid, 'Mandate Signature Date',
                    'line.mandate_id.signature_date',
                    {'line': line}, 10,
                    gen_args=gen_args, context=context)
                if sequence_type == 'FRST' and (
                        line.mandate_id.last_debit_date or
                        not line.mandate_id.sepa_migrated):
                    previous_bank = self._get_previous_bank(
                        cr, uid, line, context=context)
                    if previous_bank or not line.mandate_id.sepa_migrated:
                        amendment_indicator_2_50 = etree.SubElement(
                            mandate_related_info_2_47, 'AmdmntInd')
                        amendment_indicator_2_50.text = 'true'
                        amendment_info_details_2_51 = etree.SubElement(
                            mandate_related_info_2_47, 'AmdmntInfDtls')
                    if previous_bank:
                        if previous_bank.bank.bic == line.bank_id.bank.bic:
                            ori_debtor_account_2_57 = etree.SubElement(
                                amendment_info_details_2_51, 'OrgnlDbtrAcct')
                            ori_debtor_account_id = etree.SubElement(
                                ori_debtor_account_2_57, 'Id')
                            ori_debtor_account_iban = etree.SubElement(
                                ori_debtor_account_id, 'IBAN')
                            ori_debtor_account_iban.text = self._validate_iban(
                                cr, uid, self._prepare_field(
                                    cr, uid, 'Original Debtor Account',
                                    'previous_bank.acc_number',
                                    {'previous_bank': previous_bank},
                                    gen_args=gen_args,
                                    context=context),
                                context=context)
                        else:
                            ori_debtor_agent_2_58 = etree.SubElement(
                                amendment_info_details_2_51, 'OrgnlDbtrAgt')
                            ori_debtor_agent_institution = etree.SubElement(
                                ori_debtor_agent_2_58, 'FinInstnId')
                            ori_debtor_agent_bic = etree.SubElement(
                                ori_debtor_agent_institution, bic_xml_tag)
                            ori_debtor_agent_bic.text = self._prepare_field(
                                cr, uid, 'Original Debtor Agent',
                                'previous_bank.bank.bic',
                                {'previous_bank': previous_bank},
                                gen_args=gen_args,
                                context=context)
                            ori_debtor_agent_other = etree.SubElement(
                                ori_debtor_agent_institution, 'Othr')
                            ori_debtor_agent_other_id = etree.SubElement(
                                ori_debtor_agent_other, 'Id')
                            ori_debtor_agent_other_id.text = 'SMNDA'
                            # SMNDA = Same Mandate New Debtor Agent
                    elif not line.mandate_id.sepa_migrated:
                        ori_mandate_identification_2_52 = etree.SubElement(
                            amendment_info_details_2_51, 'OrgnlMndtId')
                        ori_mandate_identification_2_52.text = \
                            self._prepare_field(
                                cr, uid, 'Original Mandate Identification',
                                'line.mandate_id.'
                                'original_mandate_identification',
                                {'line': line},
                                gen_args=gen_args,
                                context=context)
                        ori_creditor_scheme_id_2_53 = etree.SubElement(
                            amendment_info_details_2_51, 'OrgnlCdtrSchmeId')
                        self.generate_creditor_scheme_identification(
                            cr, uid, ori_creditor_scheme_id_2_53,
                            'sepa_export.payment_order_ids[0].company_id.'
                            'original_creditor_identifier',
                            'Original Creditor Identifier',
                            {'sepa_export': sepa_export},
                            'SEPA', gen_args, context=context)

                self.generate_party_block(
                    cr, uid, dd_transaction_info_2_28, 'Dbtr', 'C',
                    'line.partner_id.name',
                    'line.bank_id.acc_number',
                    'line.bank_id.bank.bic',
                    {'line': line}, gen_args, context=context)

                self.generate_remittance_info_block(
                    cr, uid, dd_transaction_info_2_28,
                    line, gen_args, context=context)

            nb_of_transactions_2_4.text = str(transactions_count_2_4)
            control_sum_2_5.text = '%.2f' % amount_control_sum_2_5
        nb_of_transactions_1_6.text = str(transactions_count_1_6)
        control_sum_1_7.text = '%.2f' % amount_control_sum_1_7

        return self.finalize_sepa_file_creation(
            cr, uid, ids, xml_root, total_amount, transactions_count_1_6,
            gen_args, context=context)

    def cancel_sepa(self, cr, uid, ids, context=None):
        '''
        Cancel the SEPA file: just drop the file
        '''
        sepa_export = self.browse(cr, uid, ids[0], context=context)
        self.pool.get('banking.export.sdd').unlink(
            cr, uid, sepa_export.file_id.id, context=context)
        return {'type': 'ir.actions.act_window_close'}

    def save_sepa(self, cr, uid, ids, context=None):
        '''
        Save the SEPA Direct Debit file: mark all payments in the file
        as 'sent'. Write 'last debit date' on mandate and set oneoff
        mandate to expired
        '''
        sepa_export = self.browse(cr, uid, ids[0], context=context)
        self.pool.get('banking.export.sdd').write(
            cr, uid, sepa_export.file_id.id, {'state': 'sent'},
            context=context)
        wf_service = netsvc.LocalService('workflow')
        for order in sepa_export.payment_order_ids:
            wf_service.trg_validate(uid, 'payment.order', order.id, 'done', cr)
            mandate_ids = [line.mandate_id.id for line in order.line_ids]
            self.pool['account.banking.mandate'].write(
                cr, uid, mandate_ids,
                {'last_debit_date': datetime.today().strftime('%Y-%m-%d')},
                context=context)
            to_expire_ids = []
            first_mandate_ids = []
            for line in order.line_ids:
                if line.mandate_id.type == 'oneoff':
                    to_expire_ids.append(line.mandate_id.id)
                elif line.mandate_id.type == 'recurrent':
                    seq_type = line.mandate_id.recurrent_sequence_type
                    if seq_type == 'final':
                        to_expire_ids.append(line.mandate_id.id)
                    elif seq_type == 'first':
                        first_mandate_ids.append(line.mandate_id.id)
            self.pool['account.banking.mandate'].write(
                cr, uid, to_expire_ids, {'state': 'expired'}, context=context)
            self.pool['account.banking.mandate'].write(
                cr, uid, first_mandate_ids, {
                    'recurrent_sequence_type': 'recurring',
                    'sepa_migrated': True,
                }, context=context)
        return {'type': 'ir.actions.act_window_close'}
