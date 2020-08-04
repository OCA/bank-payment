# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo.tools import float_compare
import time
from lxml import etree


class TestSDD(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestSDD, cls).setUpClass()
        cls.company = cls.env['res.company']
        cls.account_model = cls.env['account.account']
        cls.move_model = cls.env['account.move']
        cls.journal_model = cls.env['account.journal']
        cls.payment_order_model = cls.env['account.payment.order']
        cls.payment_line_model = cls.env['account.payment.line']
        cls.mandate_model = cls.env['account.banking.mandate']
        cls.bank_line_model = cls.env['bank.payment.line']
        cls.partner_bank_model = cls.env['res.partner.bank']
        cls.attachment_model = cls.env['ir.attachment']
        cls.invoice_model = cls.env['account.invoice']
        cls.invoice_line_model = cls.env['account.invoice.line']
        cls.eur_currency = cls.env.ref('base.EUR')
        cls.main_company = cls.env['res.company'].create({
            'name': 'Test EUR company',
            'currency_id': cls.eur_currency.id,
            'sepa_creditor_identifier': 'FR78ZZZ424242',
        })
        cls.env.user.write({
            'company_ids': [(6, 0, cls.main_company.ids)],
            'company_id': cls.main_company.id,
        })
        chart = cls.env.ref('l10n_generic_coa.configurable_chart_template')
        wizard = cls.env['wizard.multi.charts.accounts'].create({
            'company_id': cls.main_company.id,
            'chart_template_id': chart.id,
            'code_digits': 6,
            'currency_id': cls.env.ref('base.EUR').id,
            'transfer_account_id': chart.transfer_account_id.id,
            # Set these values for not letting the dangerous default ones
            'sale_tax_id': False,
            'purchase_tax_id': False,
        })
        wizard.onchange_chart_template_id()
        wizard.execute()
        cls.partner_agrolait = cls.env.ref('base.res_partner_2')
        cls.partner_c2c = cls.env.ref('base.res_partner_12')
        cls.partner_agrolait.company_id = cls.main_company.id
        cls.partner_c2c.company_id = cls.main_company.id
        cls.account_revenue = cls.account_model.search([
            ('user_type_id', '=',
             cls.env.ref(
                 'account.data_account_type_revenue').id),
            ('company_id', '=', cls.main_company.id),
        ], limit=1)
        cls.account_receivable = cls.account_model.search([
            ('user_type_id', '=',
             cls.env.ref('account.data_account_type_receivable').id),
            ('company_id', '=', cls.main_company.id),
        ], limit=1)
        cls.company_bank = cls.env.ref(
            'account_payment_mode.main_company_iban'
        ).copy({
            'company_id': cls.main_company.id,
            'partner_id': cls.main_company.partner_id.id,
            'bank_id': (
                cls.env.ref('account_payment_mode.bank_la_banque_postale').id
            ),
        })
        # create journal
        cls.bank_journal = cls.journal_model.create({
            'name': 'Company Bank journal',
            'type': 'bank',
            'code': 'BNKFC',
            'bank_account_id': cls.company_bank.id,
            'bank_id': cls.company_bank.bank_id.id,
        })
        # update payment mode
        cls.payment_mode = cls.env.ref(
            'account_banking_sepa_direct_debit.payment_mode_inbound_sepa_dd1'
        ).copy({
            'company_id': cls.main_company.id,
        })
        cls.payment_mode.write({
            'bank_account_link': 'fixed',
            'fixed_journal_id': cls.bank_journal.id,
        })
        # Trigger the recompute of account type on res.partner.bank
        for bank_acc in cls.partner_bank_model.search([]):
            bank_acc.acc_number = bank_acc.acc_number

    def test_sdd(self):
        self.env.ref(
            'account_banking_sepa_direct_debit.res_partner_2_mandate').\
            recurrent_sequence_type = 'first'
        invoice1 = self.create_invoice(
            self.partner_agrolait.id,
            'account_banking_sepa_direct_debit.res_partner_2_mandate', 42.0)
        invoice2 = self.create_invoice(
            self.partner_c2c.id,
            'account_banking_sepa_direct_debit.res_partner_12_mandate', 11.0)
        for inv in [invoice1, invoice2]:
            action = inv.create_account_payment_line()
        self.assertEquals(action['res_model'], 'account.payment.order')
        self.payment_order = self.payment_order_model.browse(action['res_id'])
        self.assertEquals(
            self.payment_order.payment_type, 'inbound')
        self.assertEquals(
            self.payment_order.payment_mode_id, self.payment_mode)
        self.assertEquals(
            self.payment_order.journal_id, self.bank_journal)
        # Check payment line
        pay_lines = self.payment_line_model.search([
            ('partner_id', '=', self.partner_agrolait.id),
            ('order_id', '=', self.payment_order.id)])
        self.assertEquals(len(pay_lines), 1)
        agrolait_pay_line1 = pay_lines[0]
        accpre = self.env['decimal.precision'].precision_get('Account')
        self.assertEquals(
            agrolait_pay_line1.currency_id, self.eur_currency)
        self.assertEquals(
            agrolait_pay_line1.mandate_id, invoice1.mandate_id)
        self.assertEquals(
            agrolait_pay_line1.partner_bank_id,
            invoice1.mandate_id.partner_bank_id)
        self.assertEquals(float_compare(
            agrolait_pay_line1.amount_currency, 42, precision_digits=accpre),
            0)
        self.assertEquals(agrolait_pay_line1.communication_type, 'normal')
        self.assertEquals(agrolait_pay_line1.communication, invoice1.number)
        self.payment_order.draft2open()
        self.assertEquals(self.payment_order.state, 'open')
        self.assertEquals(self.payment_order.sepa, True)
        # Check bank payment line
        bank_lines = self.bank_line_model.search([
            ('partner_id', '=', self.partner_agrolait.id)])
        self.assertEquals(len(bank_lines), 1)
        agrolait_bank_line = bank_lines[0]
        self.assertEquals(
            agrolait_bank_line.currency_id, self.eur_currency)
        self.assertEquals(float_compare(
            agrolait_bank_line.amount_currency, 42.0, precision_digits=accpre),
            0)
        self.assertEquals(agrolait_bank_line.communication_type, 'normal')
        self.assertEquals(
            agrolait_bank_line.communication, invoice1.number)
        self.assertEquals(
            agrolait_bank_line.mandate_id, invoice1.mandate_id)
        self.assertEquals(
            agrolait_bank_line.partner_bank_id,
            invoice1.mandate_id.partner_bank_id)
        action = self.payment_order.open2generated()
        self.assertEquals(self.payment_order.state, 'generated')
        self.assertEquals(action['res_model'], 'ir.attachment')
        attachment = self.attachment_model.browse(action['res_id'])
        self.assertEquals(attachment.datas_fname[-4:], '.xml')
        xml_file = attachment.datas.decode('base64')
        xml_root = etree.fromstring(xml_file)
        # print "xml_file=", etree.tostring(xml_root, pretty_print=True)
        namespaces = xml_root.nsmap
        namespaces['p'] = xml_root.nsmap[None]
        namespaces.pop(None)
        pay_method_xpath = xml_root.xpath(
            '//p:PmtInf/p:PmtMtd', namespaces=namespaces)
        self.assertEquals(pay_method_xpath[0].text, 'DD')
        sepa_xpath = xml_root.xpath(
            '//p:PmtInf/p:PmtTpInf/p:SvcLvl/p:Cd', namespaces=namespaces)
        self.assertEquals(sepa_xpath[0].text, 'SEPA')
        debtor_acc_xpath = xml_root.xpath(
            '//p:PmtInf/p:CdtrAcct/p:Id/p:IBAN', namespaces=namespaces)
        self.assertEquals(
            debtor_acc_xpath[0].text,
            self.payment_order.company_partner_bank_id.sanitized_acc_number)
        self.payment_order.generated2uploaded()
        self.assertEquals(self.payment_order.state, 'uploaded')
        for inv in [invoice1, invoice2]:
            self.assertEquals(inv.state, 'paid')
        self.assertEquals(self.env.ref(
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
