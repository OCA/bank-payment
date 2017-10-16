# -*- coding: utf-8 -*-
# © 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestInvoiceMandate(TransactionCase):

    def test_post_invoice_and_refund(self):
        self.invoice._onchange_partner_id()
        self.invoice.action_invoice_open()
        self.env['account.invoice.payment.line.multi'].with_context(
            active_model='account.invoice',
            active_ids=self.invoice.ids
        ).create({}).run()

        payment_order = self.env['account.payment.order'].search([])
        self.assertEqual(len(payment_order.ids), 1)
        payment_order.draft2open()
        payment_order.open2generated()
        payment_order.generated2uploaded()

    def test_post_invoice_and_refund(self):
        self.invoice._onchange_partner_id()
        self.invoice.action_invoice_open()
        self.assertEqual(self.invoice.mandate_id, self.mandate)
        self.invoice.refund()

    def setUp(self):
        res = super(TestInvoiceMandate, self).setUp()
        self.partner = self.env.ref('base.res_partner_12')
        bank_account = self.env.ref('account_payment_mode.res_partner_12_iban')
        self.mandate = self.env['account.banking.mandate'].create({
            'partner_bank_id': bank_account.id,
            'signature_date': '2015-01-01',
        })
        self.mandate.validate()
        mode = self.env.ref('account_payment_mode.payment_mode_inbound_ct1')
        self.partner.customer_payment_mode_id = mode
        mode.payment_method_id.mandate_required = True
        invoice_account = self.env['account.account'].search(
            [('user_type_id', '=', self.env.ref(
                'account.data_account_type_payable').id)],
            limit=1).id
        invoice_line_account = self.env['account.account'].search(
            [('user_type_id', '=', self.env.ref(
                'account.data_account_type_expenses').id)],
            limit=1).id

        self.invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'account_id': invoice_account,
            'type': 'out_invoice'
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
