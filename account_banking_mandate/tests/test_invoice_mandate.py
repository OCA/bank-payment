
# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestInvoiceMandate(TransactionCase):

    def test_post_invoice_01(self):
        self.invoice._onchange_partner_id()

        self.assertEqual(self.invoice.mandate_id, self.mandate)

        self.invoice.action_invoice_open()

        payable_move_lines = self.invoice.move_id.line_ids.filtered(
            lambda s: s.account_id == self.invoice_account)
        if payable_move_lines:
            self.assertEqual(payable_move_lines[0].mandate_id, self.mandate)

        self.env['account.invoice.payment.line.multi'].with_context(
            active_model='account.invoice',
            active_ids=self.invoice.ids
        ).create({}).run()

        payment_order = self.env['account.payment.order'].search([])
        self.assertEqual(len(payment_order.ids), 1)
        payment_order.payment_mode_id_change()
        payment_order.draft2open()
        payment_order.open2generated()
        payment_order.generated2uploaded()
        self.assertEqual(self.mandate.payment_line_ids_count, 1)

    def test_post_invoice_02(self):
        partner_2 = self._create_res_partner('Jane with ACME Bank')
        partner_2.customer_payment_mode_id = self.mode_inbound_acme
        bank_account = self.env['res.partner.bank'].create({
            'acc_number': '0023032234211',
            'partner_id': partner_2.id,
            'bank_id': self.acme_bank.id,
            'company_id': self.company_2.id
        })

        mandate_2 = self.env['account.banking.mandate'].create({
            'partner_bank_id': bank_account.id,
            'signature_date': '2015-01-01',
            'company_id': self.company_2.id,
        })
        mandate_2.validate()

        self.invoice._onchange_partner_id()
        self.assertEqual(self.invoice.mandate_id, self.mandate)
        self.invoice.action_invoice_open()

        payable_move_lines = self.invoice.move_id.line_ids.filtered(
            lambda s: s.account_id == self.invoice_account)
        if payable_move_lines:
            with self.assertRaises(ValidationError):
                payable_move_lines[0].mandate_id = mandate_2

    def test_post_invoice_and_refund_02(self):
        self.invoice._onchange_partner_id()
        self.invoice.action_invoice_open()
        self.assertEqual(self.invoice.mandate_id, self.mandate)
        self.invoice.refund()

    def test_onchange_partner(self):
        partner_2 = self._create_res_partner('Jane with ACME Bank')
        partner_2.customer_payment_mode_id = self.mode_inbound_acme
        bank_account = self.env['res.partner.bank'].create({
            'acc_number': '0023032234211',
            'partner_id': partner_2.id,
            'bank_id': self.acme_bank.id,
            'company_id': self.company.id
        })

        mandate_2 = self.env['account.banking.mandate'].create({
            'partner_bank_id': bank_account.id,
            'signature_date': '2015-01-01',
            'company_id': self.company.id,
        })
        mandate_2.validate()

        invoice = self.env['account.invoice'].new({
            'partner_id': self.partner.id,
            'account_id': self.invoice_account.id,
            'type': 'out_invoice',
            'company_id': self.company.id,
        })

        invoice.partner_id = partner_2
        invoice._onchange_partner_id()
        self.assertEqual(invoice.mandate_id, mandate_2)

    def test_onchange_payment_mode(self):
        invoice = self.env['account.invoice'].new({
            'partner_id': self.partner.id,
            'account_id': self.invoice_account.id,
            'type': 'out_invoice',
            'company_id': self.company.id,
        })
        invoice._onchange_partner_id()

        pay_method_test = self.env['account.payment.method'].create({
            'name': 'Test',
            'code': 'test',
            'payment_type': 'inbound',
            'mandate_required': False
        })
        mode_inbound_acme_2 = self.env['account.payment.mode'].create({
            'name': 'Inbound Credit ACME Bank 2',
            'company_id': self.company.id,
            'bank_account_link': 'variable',
            'payment_method_id': pay_method_test.id,
        })

        invoice.payment_mode_id = mode_inbound_acme_2
        invoice._onchange_payment_mode_id()
        self.assertEqual(invoice.mandate_id, self.env[
            'account.banking.mandate'])

    def test_invoice_constrains(self):
        partner_2 = self._create_res_partner('Jane with ACME Bank')
        partner_2.customer_payment_mode_id = self.mode_inbound_acme
        bank_account = self.env['res.partner.bank'].create({
            'acc_number': '0023032234211',
            'partner_id': partner_2.id,
            'bank_id': self.acme_bank.id,
            'company_id': self.company_2.id
        })

        mandate_2 = self.env['account.banking.mandate'].create({
            'partner_bank_id': bank_account.id,
            'signature_date': '2015-01-01',
            'company_id': self.company_2.id,
        })
        mandate_2.validate()

        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'account_id': self.invoice_account.id,
            'type': 'out_invoice',
            'company_id': self.company.id,
        })

        with self.assertRaises(ValidationError):
            invoice.mandate_id = mandate_2

    def _create_res_partner(self, name):
        return self.env['res.partner'].create({
            'name': name
        })

    def _create_res_bank(self, name, bic, city, country):
        return self.env['res.bank'].create({
            'name': name,
            'bic': bic,
            'city': city,
            'country': country.id,
        })

    def setUp(self):
        res = super(TestInvoiceMandate, self).setUp()
        self.company = self.env.ref('base.main_company')

        self.partner = self._create_res_partner('Peter with ACME Bank')
        self.acme_bank = self._create_res_bank('ACME Bank', 'GEBABEBB03B',
                                               'Charleroi',
                                               self.env.ref('base.be'))

        bank_account = self.env['res.partner.bank'].create({
            'acc_number': '0023032234211123',
            'partner_id': self.partner.id,
            'bank_id': self.acme_bank.id,
            'company_id': self.company.id
        })

        self.company_2 = self.env['res.company'].create({
            'name': 'Company 2',
        })

        self.mandate = self.env['account.banking.mandate'].create({
            'partner_bank_id': bank_account.id,
            'signature_date': '2015-01-01',
            'company_id': self.company.id,
        })

        self.mandate.validate()

        self.mode_inbound_acme = self.env['account.payment.mode'].create({
            'name': 'Inbound Credit ACME Bank',
            'company_id': self.company.id,
            'bank_account_link': 'variable',
            'payment_method_id':
                self.env.ref('account.account_payment_method_manual_in').id,
        })
        bank_journal = self.env['account.journal'].search(
            [('type', '=', 'bank')], limit=1)
        self.mode_inbound_acme.variable_journal_ids = bank_journal
        self.mode_inbound_acme.payment_method_id.mandate_required = True
        self.mode_inbound_acme.payment_order_ok = True

        self.partner.customer_payment_mode_id = self.mode_inbound_acme

        self.invoice_account = self.env['account.account'].search(
            [('user_type_id', '=', self.env.ref(
                'account.data_account_type_receivable').id),
             ('company_id', '=', self.company.id)],
            limit=1)
        invoice_line_account = self.env['account.account'].search(
            [('user_type_id', '=', self.env.ref(
                'account.data_account_type_expenses').id),
             ('company_id', '=', self.company.id)],
            limit=1).id

        self.invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'account_id': self.invoice_account.id,
            'type': 'out_invoice',
            'company_id': self.company.id,
        })

        self.env['account.invoice.line'].create({
            'product_id': self.env.ref('product.product_product_4').id,
            'quantity': 1.0,
            'price_unit': 100.0,
            'invoice_id': self.invoice.id,
            'name': 'product that cost 100',
            'account_id': invoice_line_account,
        })
        return res
