# Copyright 2017 Camptocamp SA
# Copyright 2017 Creu Blanca
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import unittest
from odoo.tests.common import SavepointCase
from odoo.exceptions import ValidationError, UserError
from datetime import date, timedelta


class TestPaymentOrderInboundBase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPaymentOrderInboundBase, cls).setUpClass()
        cls.inbound_mode = cls.env.ref(
            'account_payment_mode.payment_mode_inbound_dd1'
        )
        cls.invoice_line_account = cls.env['account.account'].search(
            [('user_type_id', '=', cls.env.ref(
                'account.data_account_type_revenue').id)],
            limit=1).id
        cls.journal = cls.env['account.journal'].search(
            [('type', '=', 'bank'),
             '|', ('company_id', '=', cls.env.user.company_id.id),
             ('company_id', '=', False)], limit=1
        )
        if not cls.journal:
            raise unittest.SkipTest('No journal found')
        cls.inbound_mode.variable_journal_ids = cls.journal
        # Make sure no others orders are present
        cls.domain = [
            ('state', '=', 'draft'),
            ('payment_type', '=', 'inbound'),
        ]
        cls.payment_order_obj = cls.env['account.payment.order']
        cls.payment_order_obj.search(cls.domain).unlink()
        # Create payment order
        cls.inbound_order = cls.env['account.payment.order'].create({
            'payment_type': 'inbound',
            'payment_mode_id': cls.inbound_mode.id,
            'journal_id': cls.journal.id,
        })
        # Open invoice
        cls.invoice = cls._create_customer_invoice()
        cls.invoice.action_invoice_open()
        # Add to payment order using the wizard
        cls.env['account.invoice.payment.line.multi'].with_context(
            active_model='account.invoice',
            active_ids=cls.invoice.ids
        ).create({}).run()

    @classmethod
    def _create_customer_invoice(cls):
        invoice_account = cls.env['account.account'].search(
            [('user_type_id', '=', cls.env.ref(
                'account.data_account_type_receivable').id)],
            limit=1).id
        invoice = cls.env['account.invoice'].create({
            'partner_id': cls.env.ref('base.res_partner_4').id,
            'account_id': invoice_account,
            'type': 'out_invoice',
            'payment_mode_id': cls.inbound_mode.id
        })
        cls.env['account.invoice.line'].create({
            'product_id': cls.env.ref('product.product_product_4').id,
            'quantity': 1.0,
            'price_unit': 100.0,
            'invoice_id': invoice.id,
            'name': 'product that cost 100',
            'account_id': cls.invoice_line_account,
        })
        return invoice


class TestPaymentOrderInbound(TestPaymentOrderInboundBase):
    def test_constrains_type(self):
        with self.assertRaises(ValidationError):
            order = self.env['account.payment.order'].create({
                'payment_mode_id': self.inbound_mode.id,
                'journal_id': self.journal.id,
            })
            order.payment_type = 'outbound'

    def test_constrains_date(self):
        with self.assertRaises(ValidationError):
            self.inbound_order.date_scheduled = date.today() - timedelta(
                days=1)

    def test_creation(self):
        payment_order = self.inbound_order
        self.assertEqual(len(payment_order.ids), 1)
        # Set journal to allow cancelling entries
        self.journal.update_posted = True

        payment_order.write({
            'journal_id': self.journal.id,
        })

        self.assertEqual(len(payment_order.payment_line_ids), 1)
        self.assertEqual(len(payment_order.bank_line_ids), 0)

        # Open payment order
        payment_order.draft2open()

        self.assertEqual(payment_order.bank_line_count, 1)

        # Generate and upload
        payment_order.open2generated()
        payment_order.generated2uploaded()

        self.assertEqual(payment_order.state, 'done')
        with self.assertRaises(UserError):
            payment_order.unlink()

        bank_line = payment_order.bank_line_ids

        with self.assertRaises(UserError):
            bank_line.unlink()
        payment_order.action_done_cancel()
        self.assertEqual(payment_order.state, 'cancel')
        payment_order.cancel2draft()
        payment_order.unlink()
        self.assertEqual(len(self.payment_order_obj.search(self.domain)), 0)
