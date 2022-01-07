# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
from odoo.addons.account.tests.account_test_classes import AccountingTestCase
from odoo.tools import float_compare
import time
from lxml import etree


class TestSDD(AccountingTestCase):

    def setUp(self):
        super(TestSDD, self).setUp()
        self.company = self.env['res.company']
        self.account_model = self.env['account.account']
        self.move_model = self.env['account.move']
        self.journal_model = self.env['account.journal']
        self.payment_order_model = self.env['account.payment.order']
        self.payment_line_model = self.env['account.payment.line']
        self.mandate_model = self.env['account.banking.mandate']
        self.bank_line_model = self.env['bank.payment.line']
        self.partner_bank_model = self.env['res.partner.bank']
        self.attachment_model = self.env['ir.attachment']
        self.invoice_model = self.env['account.invoice']
        self.invoice_line_model = self.env['account.invoice.line']
        company = self.env.ref('base.main_company')
        self.partner_agrolait = self.env.ref('base.res_partner_2')
        self.partner_c2c = self.env.ref('base.res_partner_12')
        self.account_revenue = self.account_model.search([(
            'user_type_id',
            '=',
            self.env.ref('account.data_account_type_revenue').id)], limit=1)
        self.account_receivable = self.account_model.search([(
            'user_type_id',
            '=',
            self.env.ref('account.data_account_type_receivable').id)], limit=1)
        # create journal
        self.bank_journal = self.journal_model.create({
            'name': 'Company Bank journal',
            'type': 'bank',
            'code': 'BNKFC',
            'bank_account_id':
            self.env.ref('account_payment_mode.main_company_iban').id,
            'bank_id':
            self.env.ref('account_payment_mode.bank_la_banque_postale').id,
            })
        # update payment mode
        self.payment_mode = self.env.ref(
            'account_banking_sepa_direct_debit.'
            'payment_mode_inbound_sepa_dd1')
        self.payment_mode.write({
            'bank_account_link': 'fixed',
            'fixed_journal_id': self.bank_journal.id,
            })
        self.eur_currency_id = self.env.ref('base.EUR').id
        company.currency_id = self.eur_currency_id
        # Trigger the recompute of account type on res.partner.bank
        for bank_acc in self.partner_bank_model.search([]):
            bank_acc.acc_number = bank_acc.acc_number

    def test_pain_001_02(self):
        self.payment_mode.payment_method_id.pain_version = 'pain.008.001.02'
        self.check_sdd()

    def test_pain_003_02(self):
        self.payment_mode.payment_method_id.pain_version = 'pain.008.003.02'
        self.check_sdd()

    def test_pain_001_03(self):
        self.payment_mode.payment_method_id.pain_version = 'pain.008.001.03'
        self.check_sdd()

    def test_pain_001_04(self):
        self.payment_mode.payment_method_id.pain_version = 'pain.008.001.04'
        self.check_sdd()

    def check_sdd(self):
        self.env.ref(
            'account_banking_sepa_direct_debit.res_partner_2_mandate'
        ).recurrent_sequence_type = 'first'
        invoice1 = self.create_invoice(
            self.partner_agrolait.id,
            'account_banking_sepa_direct_debit.res_partner_2_mandate', 42.0)
        self.env.ref(
            'account_banking_sepa_direct_debit.res_partner_12_mandate'
        ).type = 'oneoff'
        invoice2 = self.create_invoice(
            self.partner_c2c.id,
            'account_banking_sepa_direct_debit.res_partner_12_mandate', 11.0)
        for inv in [invoice1, invoice2]:
            action = inv.create_account_payment_line()
        self.assertEqual(action['res_model'], 'account.payment.order')
        payment_order = self.payment_order_model.browse(action['res_id'])
        self.assertEqual(
            payment_order.payment_type, 'inbound')
        self.assertEqual(
            payment_order.payment_mode_id, self.payment_mode)
        self.assertEqual(
            payment_order.journal_id, self.bank_journal)
        # Check payment line
        pay_lines = self.payment_line_model.search([
            ('partner_id', '=', self.partner_agrolait.id),
            ('order_id', '=', payment_order.id)])
        self.assertEqual(len(pay_lines), 1)
        agrolait_pay_line1 = pay_lines[0]
        accpre = self.env['decimal.precision'].precision_get('Account')
        self.assertEqual(
            agrolait_pay_line1.currency_id.id, self.eur_currency_id)
        self.assertEqual(
            agrolait_pay_line1.mandate_id, invoice1.mandate_id)
        self.assertEqual(
            agrolait_pay_line1.partner_bank_id,
            invoice1.mandate_id.partner_bank_id)
        self.assertEqual(float_compare(
            agrolait_pay_line1.amount_currency, 42, precision_digits=accpre),
            0)
        self.assertEqual(agrolait_pay_line1.communication_type, 'normal')
        self.assertEqual(agrolait_pay_line1.communication, invoice1.number)
        payment_order.draft2open()
        self.assertEqual(payment_order.state, 'open')
        self.assertEqual(payment_order.sepa, True)
        # Check bank payment line
        bank_lines = self.bank_line_model.search([
            ('partner_id', '=', self.partner_agrolait.id)])
        self.assertEqual(len(bank_lines), 1)
        agrolait_bank_line = bank_lines[0]
        self.assertEqual(
            agrolait_bank_line.currency_id.id, self.eur_currency_id)
        self.assertEqual(float_compare(
            agrolait_bank_line.amount_currency, 42.0, precision_digits=accpre),
            0)
        self.assertEqual(agrolait_bank_line.communication_type, 'normal')
        self.assertEqual(
            agrolait_bank_line.communication, invoice1.number)
        self.assertEqual(
            agrolait_bank_line.mandate_id, invoice1.mandate_id)
        self.assertEqual(
            agrolait_bank_line.partner_bank_id,
            invoice1.mandate_id.partner_bank_id)
        action = payment_order.open2generated()
        self.assertEqual(payment_order.state, 'generated')
        self.assertEqual(action['res_model'], 'ir.attachment')
        attachment = self.attachment_model.browse(action['res_id'])
        self.assertEqual(attachment.datas_fname[-4:], '.xml')
        xml_file = base64.b64decode(attachment.datas)
        xml_root = etree.fromstring(xml_file)
        # print "xml_file=", etree.tostring(xml_root, pretty_print=True)
        namespaces = xml_root.nsmap
        namespaces['p'] = xml_root.nsmap[None]
        namespaces.pop(None)
        pay_method_xpath = xml_root.xpath(
            '//p:PmtInf/p:PmtMtd', namespaces=namespaces)
        self.assertEqual(pay_method_xpath[0].text, 'DD')
        sepa_xpath = xml_root.xpath(
            '//p:PmtInf/p:PmtTpInf/p:SvcLvl/p:Cd', namespaces=namespaces)
        self.assertEqual(sepa_xpath[0].text, 'SEPA')
        debtor_acc_xpath = xml_root.xpath(
            '//p:PmtInf/p:CdtrAcct/p:Id/p:IBAN', namespaces=namespaces)
        self.assertEqual(
            debtor_acc_xpath[0].text,
            payment_order.company_partner_bank_id.sanitized_acc_number)
        payment_order.generated2uploaded()
        self.assertEqual(payment_order.state, 'uploaded')
        for inv in [invoice1, invoice2]:
            self.assertEqual(inv.state, 'paid')
        self.assertEqual(self.env.ref(
            'account_banking_sepa_direct_debit.res_partner_2_mandate').
            recurrent_sequence_type, 'recurring')
        return

    def create_invoice(
            self, partner_id, mandate_xmlid, price_unit, type='out_invoice'):
        invoice = self.invoice_model.create({
            'partner_id': partner_id,
            'reference_type': 'none',
            'currency_id': self.env.ref('base.EUR').id,
            'name': 'test',
            'account_id': self.account_receivable.id,
            'type': type,
            'date_invoice': time.strftime('%Y-%m-%d'),
            'payment_mode_id': self.payment_mode.id,
            'mandate_id': self.env.ref(mandate_xmlid).id,
            })
        self.invoice_line_model.create({
            'invoice_id': invoice.id,
            'price_unit': price_unit,
            'quantity': 1,
            'name': 'Great service',
            'account_id': self.account_revenue.id,
            })
        invoice.action_invoice_open()
        return invoice
