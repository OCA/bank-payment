# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tools import float_compare
from odoo.tests import common
import time
from lxml import etree


class TestSCT(common.HttpCase):
    post_install = True
    at_install = False

    def setUp(self):
        super(TestSCT, self).setUp()
        self.account_model = self.env['account.account']
        self.move_model = self.env['account.move']
        self.journal_model = self.env['account.journal']
        self.payment_order_model = self.env['account.payment.order']
        self.payment_line_model = self.env['account.payment.line']
        self.bank_line_model = self.env['bank.payment.line']
        self.partner_bank_model = self.env['res.partner.bank']
        self.attachment_model = self.env['ir.attachment']
        self.invoice_model = self.env['account.invoice']
        self.invoice_line_model = self.env['account.invoice.line']
        self.partner_agrolait = self.env.ref('base.res_partner_2')
        self.partner_asus = self.env.ref('base.res_partner_1')
        self.partner_c2c = self.env.ref('base.res_partner_12')
        self.eur_currency = self.env.ref('base.EUR')
        self.usd_currency = self.env.ref('base.USD')
        self.main_company = self.env['res.company'].create({
            'name': 'Test EUR company',
            'currency_id': self.eur_currency.id,
        })
        self.env.user.write({
            'company_ids': [(6, 0, self.main_company.ids)],
            'company_id': self.main_company.id,
        })
        self.env.ref(
            'l10n_generic_coa.configurable_chart_template'
        ).try_loading_for_current_company()
        self.account_expense = self.account_model.search([
            ('user_type_id', '=',
             self.env.ref('account.data_account_type_expenses').id),
            ('company_id', '=', self.main_company.id),
        ], limit=1)
        self.account_payable = self.account_model.search([
            ('user_type_id', '=',
             self.env.ref('account.data_account_type_payable').id),
            ('company_id', '=', self.main_company.id),
        ], limit=1)
        self.partner_bank = self.env.ref(
            'account_payment_mode.main_company_iban'
        ).copy({
            'company_id': self.main_company.id,
            'partner_id': self.main_company.partner_id.id,
            'bank_id': (
                self.env.ref('account_payment_mode.bank_la_banque_postale').id
            ),
        })
        # create journal
        self.bank_journal = self.journal_model.create({
            'name': 'Company Bank journal',
            'type': 'bank',
            'code': 'BNKFB',
            'bank_account_id': self.partner_bank.id,
            'bank_id': self.partner_bank.bank_id.id,
        })
        # update payment mode
        self.payment_mode = self.env.ref(
            'account_banking_sepa_credit_transfer.'
            'payment_mode_outbound_sepa_ct1'
        ).copy({
            'company_id': self.main_company.id,
        })
        self.payment_mode.write({
            'bank_account_link': 'fixed',
            'fixed_journal_id': self.bank_journal.id,
        })
        # Trigger the recompute of account type on res.partner.bank
        for bank_acc in self.partner_bank_model.search([]):
            bank_acc.acc_number = bank_acc.acc_number

    def test_eur_currency_sct(self):
        invoice1 = self.create_invoice(
            self.partner_agrolait.id,
            'account_payment_mode.res_partner_2_iban', self.eur_currency.id,
            42.0, 'F1341')
        invoice2 = self.create_invoice(
            self.partner_agrolait.id,
            'account_payment_mode.res_partner_2_iban', self.eur_currency.id,
            12.0, 'F1342')
        invoice3 = self.create_invoice(
            self.partner_agrolait.id,
            'account_payment_mode.res_partner_2_iban', self.eur_currency.id,
            5.0, 'A1301', 'in_refund')
        invoice4 = self.create_invoice(
            self.partner_c2c.id,
            'account_payment_mode.res_partner_12_iban', self.eur_currency.id,
            11.0, 'I1642')
        invoice5 = self.create_invoice(
            self.partner_c2c.id,
            'account_payment_mode.res_partner_12_iban', self.eur_currency.id,
            41.0, 'I1643')
        for inv in [invoice1, invoice2, invoice3, invoice4, invoice5]:
            action = inv.create_account_payment_line()
        self.assertEquals(action['res_model'], 'account.payment.order')
        self.payment_order = self.payment_order_model.browse(action['res_id'])
        self.assertEquals(
            self.payment_order.payment_type, 'outbound')
        self.assertEquals(
            self.payment_order.payment_mode_id, self.payment_mode)
        self.assertEquals(
            self.payment_order.journal_id, self.bank_journal)
        pay_lines = self.payment_line_model.search([
            ('partner_id', '=', self.partner_agrolait.id),
            ('order_id', '=', self.payment_order.id)])
        self.assertEquals(len(pay_lines), 3)
        agrolait_pay_line1 = pay_lines[0]
        accpre = self.env['decimal.precision'].precision_get('Account')
        self.assertEquals(agrolait_pay_line1.currency_id, self.eur_currency)
        self.assertEquals(
            agrolait_pay_line1.partner_bank_id, invoice1.partner_bank_id)
        self.assertEquals(float_compare(
            agrolait_pay_line1.amount_currency, 42, precision_digits=accpre),
            0)
        self.assertEquals(agrolait_pay_line1.communication_type, 'normal')
        self.assertEquals(agrolait_pay_line1.communication, 'F1341')
        self.payment_order.draft2open()
        self.assertEquals(self.payment_order.state, 'open')
        self.assertEquals(self.payment_order.sepa, True)
        bank_lines = self.bank_line_model.search([
            ('partner_id', '=', self.partner_agrolait.id)])
        self.assertEquals(len(bank_lines), 1)
        agrolait_bank_line = bank_lines[0]
        self.assertEquals(agrolait_bank_line.currency_id, self.eur_currency)
        self.assertEquals(float_compare(
            agrolait_bank_line.amount_currency, 49.0, precision_digits=accpre),
            0)
        self.assertEquals(agrolait_bank_line.communication_type, 'normal')
        self.assertEquals(
            agrolait_bank_line.communication, 'F1341-F1342-A1301')
        self.assertEquals(
            agrolait_bank_line.partner_bank_id, invoice1.partner_bank_id)

        action = self.payment_order.open2generated()
        self.assertEquals(self.payment_order.state, 'generated')
        self.assertEquals(action['res_model'], 'ir.attachment')
        attachment = self.attachment_model.browse(action['res_id'])
        self.assertEquals(attachment.datas_fname[-4:], '.xml')
        xml_file = attachment.datas.decode('base64')
        xml_root = etree.fromstring(xml_file)
        namespaces = xml_root.nsmap
        namespaces['p'] = xml_root.nsmap[None]
        namespaces.pop(None)
        pay_method_xpath = xml_root.xpath(
            '//p:PmtInf/p:PmtMtd', namespaces=namespaces)
        self.assertEquals(pay_method_xpath[0].text, 'TRF')
        sepa_xpath = xml_root.xpath(
            '//p:PmtInf/p:PmtTpInf/p:SvcLvl/p:Cd', namespaces=namespaces)
        self.assertEquals(sepa_xpath[0].text, 'SEPA')
        debtor_acc_xpath = xml_root.xpath(
            '//p:PmtInf/p:DbtrAcct/p:Id/p:IBAN', namespaces=namespaces)
        self.assertEquals(
            debtor_acc_xpath[0].text,
            self.payment_order.company_partner_bank_id.sanitized_acc_number)
        self.payment_order.generated2uploaded()
        self.assertEquals(self.payment_order.state, 'uploaded')
        for inv in [invoice1, invoice2, invoice3, invoice4, invoice5]:
            self.assertEquals(inv.state, 'paid')
        return

    def test_usd_currency_sct(self):
        invoice1 = self.create_invoice(
            self.partner_asus.id,
            'account_payment_mode.res_partner_2_iban', self.usd_currency.id,
            2042.0, 'Inv9032')
        invoice2 = self.create_invoice(
            self.partner_asus.id,
            'account_payment_mode.res_partner_2_iban', self.usd_currency.id,
            1012.0, 'Inv9033')
        for inv in [invoice1, invoice2]:
            action = inv.create_account_payment_line()
        self.assertEquals(action['res_model'], 'account.payment.order')
        self.payment_order = self.payment_order_model.browse(action['res_id'])
        self.assertEquals(
            self.payment_order.payment_type, 'outbound')
        self.assertEquals(
            self.payment_order.payment_mode_id, self.payment_mode)
        self.assertEquals(
            self.payment_order.journal_id, self.bank_journal)
        pay_lines = self.payment_line_model.search([
            ('partner_id', '=', self.partner_asus.id),
            ('order_id', '=', self.payment_order.id)])
        self.assertEquals(len(pay_lines), 2)
        asus_pay_line1 = pay_lines[0]
        accpre = self.env['decimal.precision'].precision_get('Account')
        self.assertEquals(asus_pay_line1.currency_id, self.usd_currency)
        self.assertEquals(
            asus_pay_line1.partner_bank_id, invoice1.partner_bank_id)
        self.assertEquals(float_compare(
            asus_pay_line1.amount_currency, 2042, precision_digits=accpre),
            0)
        self.assertEquals(asus_pay_line1.communication_type, 'normal')
        self.assertEquals(asus_pay_line1.communication, 'Inv9032')
        self.payment_order.draft2open()
        self.assertEquals(self.payment_order.state, 'open')
        self.assertEquals(self.payment_order.sepa, False)
        bank_lines = self.bank_line_model.search([
            ('partner_id', '=', self.partner_asus.id)])
        self.assertEquals(len(bank_lines), 1)
        asus_bank_line = bank_lines[0]
        self.assertEquals(asus_bank_line.currency_id, self.usd_currency)
        self.assertEquals(float_compare(
            asus_bank_line.amount_currency, 3054.0, precision_digits=accpre),
            0)
        self.assertEquals(asus_bank_line.communication_type, 'normal')
        self.assertEquals(
            asus_bank_line.communication, 'Inv9032-Inv9033')
        self.assertEquals(
            asus_bank_line.partner_bank_id, invoice1.partner_bank_id)

        action = self.payment_order.open2generated()
        self.assertEquals(self.payment_order.state, 'generated')
        self.assertEquals(action['res_model'], 'ir.attachment')
        attachment = self.attachment_model.browse(action['res_id'])
        self.assertEquals(attachment.datas_fname[-4:], '.xml')
        xml_file = attachment.datas.decode('base64')
        xml_root = etree.fromstring(xml_file)
        namespaces = xml_root.nsmap
        namespaces['p'] = xml_root.nsmap[None]
        namespaces.pop(None)
        pay_method_xpath = xml_root.xpath(
            '//p:PmtInf/p:PmtMtd', namespaces=namespaces)
        self.assertEquals(pay_method_xpath[0].text, 'TRF')
        sepa_xpath = xml_root.xpath(
            '//p:PmtInf/p:PmtTpInf/p:SvcLvl/p:Cd', namespaces=namespaces)
        self.assertEquals(len(sepa_xpath), 0)
        debtor_acc_xpath = xml_root.xpath(
            '//p:PmtInf/p:DbtrAcct/p:Id/p:IBAN', namespaces=namespaces)
        self.assertEquals(
            debtor_acc_xpath[0].text,
            self.payment_order.company_partner_bank_id.sanitized_acc_number)
        self.payment_order.generated2uploaded()
        self.assertEquals(self.payment_order.state, 'uploaded')
        for inv in [invoice1, invoice2]:
            self.assertEquals(inv.state, 'paid')
        return

    def create_invoice(
            self, partner_id, partner_bank_xmlid, currency_id,
            price_unit, reference, type='in_invoice'):
        invoice = self.invoice_model.create({
            'partner_id': partner_id,
            'reference_type': 'none',
            'reference': reference,
            'currency_id': currency_id,
            'name': 'test',
            'account_id': self.account_payable.id,
            'type': type,
            'date_invoice': time.strftime('%Y-%m-%d'),
            'payment_mode_id': self.payment_mode.id,
            'partner_bank_id': self.env.ref(partner_bank_xmlid).id,
            })
        self.invoice_line_model.create({
            'invoice_id': invoice.id,
            'price_unit': price_unit,
            'quantity': 1,
            'name': 'Great service',
            'account_id': self.account_expense.id,
            })
        invoice.action_invoice_open()
        return invoice
