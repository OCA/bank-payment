# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPaymentOrder(TransactionCase):

    def setUp(self):
        super(TestPaymentOrder, self).setUp()
        self.AccountObj = self.env['account.account']
        self.InvoiceObj = self.env['account.invoice']
        self.PaymentOrderInvoiceCancelObj = self.env[
            'account.payment.order.invoice_cancel']

    def _create_supplier_invoice(self):
        invoice_account = self.AccountObj.search(
            [('user_type_id', '=', self.env.ref(
                'account.data_account_type_payable').id)],
            limit=1).id
        invoice_line_account = self.env['account.account'].search(
            [('user_type_id', '=', self.env.ref(
                'account.data_account_type_expenses').id)],
            limit=1).id

        invoice = self.InvoiceObj.create({
            'partner_id': self.env.ref('base.res_partner_4').id,
            'account_id': invoice_account,
            'type': 'in_invoice',
            'payment_mode_id': self.env.ref(
                'account_payment_mode.payment_mode_outbound_ct1').id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.env.ref('product.product_product_4').id,
                    'quantity': 1.0,
                    'price_unit': 100.0,
                    'name': 'Test',
                    'account_id': invoice_line_account,
                })
            ]
        })
        return invoice

    def test_cancel_payment_order(self):
        # Open invoice
        invoice = self._create_supplier_invoice()
        invoice.action_invoice_open()
        # Add to payment order
        invoice.create_account_payment_line()

        invoice.move_id.journal_id.update_posted = True
        cancel_res = invoice.action_cancel()
        self.assertTrue(isinstance(cancel_res, dict))
        self.assertEqual(invoice.state, 'open')

        wizard = self.PaymentOrderInvoiceCancelObj.create({
            'invoice_ids': [(6, 0, invoice.ids)]
        })
        wizard.doit()
        invoice.action_cancel()
        self.assertEqual(invoice.state, 'cancel')
