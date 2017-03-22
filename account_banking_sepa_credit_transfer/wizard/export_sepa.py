# -*- coding: utf-8 -*-
##############################################################################
#
#    SEPA Credit Transfer module for OpenERP
#    Copyright (C) 2010-2013 Akretion (http://www.akretion.com)
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
from lxml import etree


class banking_export_sepa_wizard(orm.TransientModel):
    _name = 'banking.export.sepa.wizard'
    _inherit = ['banking.export.pain']
    _description = 'Export SEPA Credit Transfer File'

    _columns = {
        'state': fields.selection(
            [
                ('create', 'Create'),
                ('finish', 'Finish'),
            ],
            'State', readonly=True),
        'batch_booking': fields.boolean(
            'Batch Booking',
            help="If true, the bank statement will display only one debit "
            "line for all the wire transfers of the SEPA XML file ; if "
            "false, the bank statement will display one debit line per wire "
            "transfer of the SEPA XML file."),
        'charge_bearer': fields.selection(
            [
                ('SLEV', 'Following Service Level'),
                ('SHAR', 'Shared'),
                ('CRED', 'Borne by Creditor'),
                ('DEBT', 'Borne by Debtor'),
            ],
            'Charge Bearer', required=True,
            help="Following service level : transaction charges are to be "
            "applied following the rules agreed in the service level and/or "
            "scheme (SEPA Core messages must use this). Shared : transaction "
            "charges on the debtor side are to be borne by the debtor, "
            "transaction charges on the creditor side are to be borne by "
            "the creditor. Borne by creditor : all transaction charges are "
            "to be borne by the creditor. Borne by debtor : all transaction "
            "charges are to be borne by the debtor."),
        'nb_transactions': fields.related(
            'file_id', 'nb_transactions', type='integer',
            string='Number of Transactions', readonly=True),
        'total_amount': fields.related(
            'file_id', 'total_amount', type='float', string='Total Amount',
            readonly=True),
        'file_id': fields.many2one(
            'banking.export.sepa', 'SEPA XML File', readonly=True),
        'file': fields.related(
            'file_id', 'file', string="File", type='binary', readonly=True),
        'filename': fields.related(
            'file_id', 'filename', string="Filename", type='char',
            size=256, readonly=True),
        'payment_order_ids': fields.many2many(
            'payment.order', 'wiz_sepa_payorders_rel', 'wizard_id',
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
        return super(banking_export_sepa_wizard, self).create(
            cr, uid, vals, context=context)

    def create_sepa(self, cr, uid, ids, context=None):
        '''
        Creates the SEPA Credit Transfer file. That's the important code !
        '''
        if context is None:
            context = {}
        sepa_export = self.browse(cr, uid, ids[0], context=context)
        pain_flavor = sepa_export.payment_order_ids[0].mode.type.code
        convert_to_ascii = \
            sepa_export.payment_order_ids[0].mode.convert_to_ascii
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
            raise orm.except_orm(
                _('Error:'),
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
            'pain_flavor': pain_flavor,
            'sepa_export': sepa_export,
            'file_obj': self.pool['banking.export.sepa'],
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
            self.generate_group_header_block(
                cr, uid, pain_root, gen_args, context=context)

        transactions_count_1_6 = 0
        total_amount = 0.0
        amount_control_sum_1_7 = 0.0
        lines_per_group = {}
        # key = (requested_date, priority)
        # values = list of lines as object
        today = fields.date.context_today(self, cr, uid, context=context)
        for payment_order in sepa_export.payment_order_ids:
            total_amount = total_amount + payment_order.total
            for line in payment_order.line_ids:
                priority = line.priority
                if payment_order.date_prefered == 'due':
                    requested_date = line.ml_maturity_date or today
                elif payment_order.date_prefered == 'fixed':
                    requested_date = payment_order.date_scheduled or today
                else:
                    requested_date = today
                key = (requested_date, priority)
                if key in lines_per_group:
                    lines_per_group[key].append(line)
                else:
                    lines_per_group[key] = [line]
                # Write requested_date on 'Payment date' of the pay line
                if requested_date != line.date:
                    self.pool['payment.line'].write(
                        cr, uid, line.id,
                        {'date': requested_date}, context=context)

        for (requested_date, priority), lines in lines_per_group.items():
            # B. Payment info
            payment_info_2_0, nb_of_transactions_2_4, control_sum_2_5 = \
                self.generate_start_payment_info_block(
                    cr, uid, pain_root,
                    "sepa_export.payment_order_ids[0].reference + '-' "
                    "+ requested_date.replace('-', '')  + '-' + priority",
                    priority, False, False, requested_date, {
                        'sepa_export': sepa_export,
                        'priority': priority,
                        'requested_date': requested_date,
                    }, gen_args, context=context)

            self.generate_party_block(
                cr, uid, payment_info_2_0, 'Dbtr', 'B',
                'sepa_export.payment_order_ids[0].mode.bank_id.partner_id.'
                'name',
                'sepa_export.payment_order_ids[0].mode.bank_id.acc_number',
                'sepa_export.payment_order_ids[0].mode.bank_id.bank.bic',
                {'sepa_export': sepa_export},
                gen_args, context=context)

            charge_bearer_2_24 = etree.SubElement(payment_info_2_0, 'ChrgBr')
            charge_bearer_2_24.text = sepa_export.charge_bearer

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
                    cr, uid, 'End to End Identification', 'line.name',
                    {'line': line}, 35, gen_args=gen_args,
                    context=context)
                currency_name = self._prepare_field(
                    cr, uid, 'Currency Code', 'line.currency.name',
                    {'line': line}, 3, gen_args=gen_args,
                    context=context)
                amount_2_42 = etree.SubElement(
                    credit_transfer_transaction_info_2_27, 'Amt')
                instructed_amount_2_43 = etree.SubElement(
                    amount_2_42, 'InstdAmt', Ccy=currency_name)
                instructed_amount_2_43.text = '%.2f' % line.amount_currency
                amount_control_sum_1_7 += line.amount_currency
                amount_control_sum_2_5 += line.amount_currency

                if not line.bank_id:
                    raise orm.except_orm(
                        _('Error:'),
                        _("Missing Bank Account on invoice '%s' (payment "
                            "order line reference '%s').")
                        % (line.ml_inv_ref.number, line.name))
                self.generate_party_block(
                    cr, uid, credit_transfer_transaction_info_2_27, 'Cdtr',
                    'C', 'line.partner_id.name', 'line.bank_id.acc_number',
                    'line.bank_id.bank.bic', {'line': line}, gen_args,
                    context=context)

                self.generate_remittance_info_block(
                    cr, uid, credit_transfer_transaction_info_2_27,
                    line, gen_args, context=context)

            if pain_flavor in pain_03_to_05:
                nb_of_transactions_2_4.text = str(transactions_count_2_4)
                control_sum_2_5.text = '%.2f' % amount_control_sum_2_5

        if pain_flavor in pain_03_to_05:
            nb_of_transactions_1_6.text = str(transactions_count_1_6)
            control_sum_1_7.text = '%.2f' % amount_control_sum_1_7
        else:
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
        self.pool.get('banking.export.sepa').unlink(
            cr, uid, sepa_export.file_id.id, context=context)
        return {'type': 'ir.actions.act_window_close'}

    def save_sepa(self, cr, uid, ids, context=None):
        '''
        Save the SEPA file: send the done signal to all payment
        orders in the file. With the default workflow, they will
        transition to 'done', while with the advanced workflow in
        account_banking_payment they will transition to 'sent' waiting
        reconciliation.
        '''
        sepa_export = self.browse(cr, uid, ids[0], context=context)
        self.pool.get('banking.export.sepa').write(
            cr, uid, sepa_export.file_id.id, {'state': 'sent'},
            context=context)
        wf_service = netsvc.LocalService('workflow')
        for order in sepa_export.payment_order_ids:
            wf_service.trg_validate(uid, 'payment.order', order.id, 'done', cr)
        return {'type': 'ir.actions.act_window_close'}
