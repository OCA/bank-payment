# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.tools import float_compare
from odoo.exceptions import ValidationError


class TestPaymentOrderCheck(TransactionCase):
    def setUp(self):
        super().setUp()
        self.eur_currency = self.env.ref('base.EUR')
        self.payment_order_model = self.env['account.payment.order']
        self.payment_line_model = self.env['account.payment.line']
        self.journal_model = self.env['account.journal']
        self.bank_line_model = self.env['bank.payment.line']
        self.attachment_model = self.env['ir.attachment']
        self.account_model = self.env['account.account']
        self.partner_bank_model = self.env['res.partner.bank']
        self.layout = self.browse_ref(
            'account_check_printing_report_base.'
            'account_payment_check_report_base')
        self.main_company = self.env['res.company'].create({
            'name': 'Test EUR company',
            'currency_id': self.eur_currency.id,
            'check_layout_id': self.layout.id,
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
        # create journal
        self.partner_bank = self.env.ref(
            'account_payment_mode.main_company_iban'
        ).copy({
            'company_id': self.main_company.id,
            'partner_id': self.main_company.partner_id.id,
            'bank_id': self.browse_ref(
                'account_payment_mode.bank_la_banque_postale').id,
        })
        self.bank_journal = self.journal_model.create({
            'name': 'Company Bank journal',
            'type': 'bank',
            'code': 'BNKFB',
            'bank_account_id': self.partner_bank.id,
            'bank_id': self.partner_bank.bank_id.id,

        })
        self.payment_mode = self.env['account.payment.mode'].create({
            'company_id': self.main_company.id,
            'name': 'Check',
            'payment_method_id': self.browse_ref(
                'account_check_printing.account_payment_method_check').id,
            'check_layout_id': self.layout.id,
            'bank_account_link': 'fixed',
            'fixed_journal_id': self.bank_journal.id,
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Partner',
        })

    def test_check(self):
        invoice1 = self.create_invoice(
            self.partner.id,
            'account_payment_mode.res_partner_2_iban', self.eur_currency.id,
            2042.0, 'Inv9032')
        invoice2 = self.create_invoice(
            self.partner.id,
            'account_payment_mode.res_partner_2_iban', self.eur_currency.id,
            1012.0, 'Inv9033')
        for inv in [invoice1, invoice2]:
            action = inv.create_account_payment_line()
        self.assertEqual(action['res_model'], 'account.payment.order')
        self.payment_order = self.payment_order_model.browse(action['res_id'])
        self.assertEqual(
            self.payment_order.payment_type, 'outbound')
        self.assertEqual(
            self.payment_order.payment_mode_id, self.payment_mode)
        self.assertEqual(
            self.payment_order.journal_id, self.bank_journal)
        pay_lines = self.payment_line_model.search([
            ('partner_id', '=', self.partner.id),
            ('order_id', '=', self.payment_order.id)])
        self.assertEqual(len(pay_lines), 2)
        asus_pay_line1 = pay_lines[0]
        accpre = self.env['decimal.precision'].precision_get('Account')
        self.assertEqual(asus_pay_line1.currency_id, self.eur_currency)
        self.assertEqual(
            asus_pay_line1.partner_bank_id, invoice1.partner_bank_id)
        self.assertEqual(float_compare(
            asus_pay_line1.amount_currency, 2042, precision_digits=accpre),
            0)
        self.assertEqual(asus_pay_line1.communication_type, 'normal')
        self.assertEqual(asus_pay_line1.communication, 'Inv9032')
        self.payment_order.draft2open()
        self.assertEqual(self.payment_order.state, 'open')
        bank_lines = self.bank_line_model.search([
            ('partner_id', '=', self.partner.id)])
        self.assertEqual(len(bank_lines), 1)
        asus_bank_line = bank_lines[0]
        self.assertEqual(asus_bank_line.currency_id, self.eur_currency)
        self.assertEqual(float_compare(
            asus_bank_line.amount_currency, 3054.0, precision_digits=accpre),
            0)
        self.assertEqual(asus_bank_line.communication_type, 'normal')
        self.assertEqual(
            asus_bank_line.communication, 'Inv9032-Inv9033')
        self.assertEqual(
            asus_bank_line.partner_bank_id, invoice1.partner_bank_id)

        action = self.payment_order.open2generated()
        self.assertEqual(self.payment_order.state, 'generated')
        self.assertEqual(action['res_model'], 'ir.attachment')
        attachment = self.attachment_model.browse(action['res_id'])
        self.assertEqual(attachment.datas_fname[-4:], '.pdf')

    def create_invoice(
            self, partner_id, partner_bank_xmlid, currency_id,
            price_unit, reference, type='in_invoice'):
        invoice = self.env['account.invoice'].create({
            'partner_id': partner_id,
            'reference_type': 'none',
            'reference': reference,
            'currency_id': currency_id,
            'name': 'test',
            'account_id': self.account_payable.id,
            'type': type,
            'payment_mode_id': self.payment_mode.id,
            'partner_bank_id': self.env.ref(partner_bank_xmlid).id,
            })
        self.env['account.invoice.line'].create({
            'invoice_id': invoice.id,
            'price_unit': price_unit,
            'quantity': 1,
            'name': 'Great service',
            'account_id': self.account_expense.id,
            })
        invoice.action_invoice_open()
        return invoice

    def test_constrain(self):
        with self.assertRaises(ValidationError):
            self.payment_mode.check_layout_id = False
