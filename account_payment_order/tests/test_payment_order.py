# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from datetime import datetime


class TestPaymentOrder(TransactionCase):

    def setUp(self):
        super(TestPaymentOrder, self).setUp()
        self.invoice = self._create_supplier_invoice()

    def _create_supplier_invoice(self):
        invoice_account = self.env['account.account'].search(
            [('user_type_id', '=', self.env.ref(
                'account.data_account_type_payable').id)],
            limit=1).id
        self.invoice_line_account = self.env['account.account'].search(
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
            'account_id': self.invoice_line_account,
        })

        return invoice

    def test_creation(self):
        # Open invoice
        self.invoice.action_invoice_open()
        mode = self.env.ref('account_payment_mode.payment_mode_outbound_ct1')
        order = self.env['account.payment.order'].create({
            'payment_type': 'outbound',
            'payment_mode_id': self.env.ref(
                'account_payment_mode.payment_mode_outbound_dd1').id
        })
        bank_journal = self.env['account.journal'].search(
            [('type', '=', 'bank')], limit=1)
        mode.variable_journal_ids = bank_journal
        order.payment_mode_id = mode.id
        order.payment_mode_id_change()
        self.assertEqual(order.journal_id.id, bank_journal.id)

        self.assertEqual(len(order.payment_line_ids), 0)
        line_create = self.env['account.payment.line.create'].with_context(
            active_model='account.payment.order',
            active_id=order.id
        ).create({})
        line_create.date_type = 'move'
        line_create.move_date = datetime.now()
        line_create.payment_mode = 'any'
        line_create.move_line_filters_change()
        line_create.populate()
        line_create.create_payment_lines()
        line_create_due = self.env['account.payment.line.create'].with_context(
            active_model='account.payment.order',
            active_id=order.id
        ).create({})
        line_create_due.date_type = 'due'
        line_create_due.due_date = datetime.now()
        line_create_due.populate()
        line_create_due.create_payment_lines()
        self.assertGreater(len(order.payment_line_ids), 0)

    def test_cancel_payment_order(self):
        # Open invoice
        self.invoice.action_invoice_open()
        # Add to payment order using the wizard
        self.env['account.invoice.payment.line.multi'].with_context(
            active_model='account.invoice',
            active_ids=self.invoice.ids
        ).create({}).run()

        payment_order = self.env['account.payment.order'].search([])
        self.assertEqual(len(payment_order.ids), 1)
        bank_journal = self.env['account.journal'].search(
            [('type', '=', 'bank')], limit=1)
        # Set journal to allow cancelling entries
        bank_journal.update_posted = True

        payment_order.write({
            'journal_id': bank_journal.id
        })

        self.assertEqual(len(payment_order.payment_line_ids), 1)
        self.assertEqual(len(payment_order.bank_line_ids), 0)

        # Open payment order
        payment_order.draft2open()

        self.assertEqual(payment_order.bank_line_count, 1)

        # Generate and upload
        payment_order.open2generated()
        payment_order.generated2uploaded()

        self.assertEqual(payment_order.state, 'uploaded')
        with self.assertRaises(UserError):
            payment_order.unlink()

        bank_line = payment_order.bank_line_ids

        with self.assertRaises(UserError):
            bank_line.unlink()
        payment_order.action_done_cancel()
        self.assertEqual(payment_order.state, 'cancel')
        payment_order.cancel2draft()

        payment_order.unlink()
        self.assertEqual(len(self.env['account.payment.order'].search([])), 0)
