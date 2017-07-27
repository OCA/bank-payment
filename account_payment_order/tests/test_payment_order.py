# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.exceptions import UserError


class TestPaymentOrder(TransactionCase):

    def setUp(self):
        super(TestPaymentOrder, self).setUp()
        self.invoice = self._create_supplier_invoice()

    def _create_supplier_invoice(self):
        invoice_account = self.env['account.account'].search(
            [('user_type_id', '=', self.env.ref(
                'account.data_account_type_payable').id)],
            limit=1).id
        invoice_line_account = self.env['account.account'].search(
            [('user_type_id', '=', self.env.ref(
                'account.data_account_type_expenses').id)],
            limit=1).id

        invoice = self.env['account.invoice'].create({
            'partner_id': self.env.ref('base.res_partner_4').id,
            'account_id': invoice_account,
            'type': 'in_invoice',
            'payment_mode_id': self.env.ref(
                'account_payment_mode.payment_mode_outbound_ct1').id
        })

        self.env['account.invoice.line'].create({
            'product_id': self.env.ref('product.product_product_4').id,
            'quantity': 1.0,
            'price_unit': 100.0,
            'invoice_id': invoice.id,
            'name': 'product that cost 100',
            'account_id': invoice_line_account,
        })

        return invoice

    def test_cancel_payment_order(self):
        # Open invoice
        self.invoice.signal_workflow('invoice_open')
        # Add to payment order
        self.invoice.create_account_payment_line()

        payment_order = self.env['account.payment.order'].search([])
        bank_journal = self.env['account.journal'].search(
            [('type', '=', 'bank')])
        # Set journal to allow cancelling entries
        bank_journal.update_posted = True

        payment_order.write({
            'journal_id': bank_journal.id
        })

        self.assertEquals(len(payment_order.payment_line_ids), 1)
        self.assertEquals(len(payment_order.bank_line_ids), 0)

        # Open payment order
        payment_order.draft2open()

        self.assertEquals(len(payment_order.bank_line_ids), 1)

        # Generate and upload
        payment_order.open2generated()
        payment_order.generated2uploaded()

        self.assertEquals(payment_order.state, 'uploaded')
        with self.assertRaises(UserError):
            payment_order.unlink()

        bank_line = payment_order.bank_line_ids

        with self.assertRaises(UserError):
            bank_line.unlink()

        payment_order.action_done_cancel()
        self.assertEquals(payment_order.state, 'cancel')

        payment_order.unlink()
        self.assertEquals(len(self.env['account.payment.order'].search([])), 0)
