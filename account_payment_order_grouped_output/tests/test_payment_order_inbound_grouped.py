# Copyright 2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from freezegun import freeze_time

from odoo import fields
from odoo.tests.common import tagged

from odoo.addons.account.models.account_move_line import AccountMoveLine
from odoo.addons.account_payment_order.tests.test_payment_order_inbound import (
    TestPaymentOrderInboundBase,
)

from ..models.account_payment_order import AccountPaymentOrder


@tagged("post_install", "-at_install")
class TestPaymentOrderInbound(TestPaymentOrderInboundBase):
    @freeze_time("2024-04-01")
    def test_grouped_output(self):
        self.inbound_mode.generate_move = True
        self.inbound_mode.post_move = True
        self.inbound_order.date_prefered = "fixed"
        self.inbound_order.date_scheduled = "2024-08-01"
        self.inbound_order.draft2open()
        self.inbound_order.open2generated()
        self.inbound_order.generated2uploaded()
        grouped_moves = self.inbound_order.grouped_move_ids
        self.assertFalse(grouped_moves)
        # Add now a second line with different partner
        self.inbound_order.action_uploaded_cancel()
        self.inbound_order.cancel2draft()
        old_partner = self.partner
        self.partner = self.env["res.partner"].create({"name": "Test Partner 2"})
        invoice2 = self._create_customer_invoice()
        self.partner = old_partner
        invoice2.action_post()
        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=invoice2.ids
        ).create({}).run()
        self.inbound_order.draft2open()
        self.inbound_order.open2generated()
        self.inbound_order.generated2uploaded()
        grouped_moves = self.inbound_order.grouped_move_ids
        self.assertTrue(grouped_moves)
        self.assertTrue(grouped_moves.line_ids[0].reconciled)
        self.assertTrue(
            all(
                x.date_maturity == fields.Date.from_string("2024-08-01")
                for x in grouped_moves.line_ids
            )
        )
        self.assertEqual(self.inbound_order.grouped_move_count, 1)
        self.inbound_order.action_uploaded_cancel()
        self.assertFalse(self.inbound_order.grouped_move_count)

    @freeze_time("2024-04-01")
    def test_reconcile_grouped_payments_in_batches(self):
        self.inbound_mode.generate_move = True
        self.inbound_mode.post_move = True
        self.inbound_order.date_prefered = "fixed"
        self.inbound_order.date_scheduled = "2024-08-01"
        old_partner = self.partner
        for i in range(4):
            self.partner = self.env["res.partner"].create({"name": f"Test Partner {i}"})
            invoice = self._create_customer_invoice()
            invoice.action_post()
            self.env["account.invoice.payment.line.multi"].with_context(
                active_model="account.move", active_ids=invoice.ids
            ).create({}).run()
        self.partner = old_partner
        self.inbound_order.draft2open()
        self.inbound_order.open2generated()
        self.assertEqual(len(self.inbound_order.payment_ids), 5)

        original_reconcile = AccountMoveLine.reconcile
        with (
            patch.object(
                AccountPaymentOrder,
                "_get_reconcile_grouped_payments_batch_size",
                return_value=2,
            ),
            patch.object(
                AccountMoveLine,
                "reconcile",
                autospec=True,
                side_effect=original_reconcile,
            ) as reconcile_mock,
        ):
            self.inbound_order.generated2uploaded()

        self.assertEqual(reconcile_mock.call_count, 8)
        grouped_moves = self.inbound_order.grouped_move_ids
        self.assertTrue(grouped_moves)
        self.assertTrue(all(grouped_moves.line_ids[:-1].mapped("reconciled")))

    @freeze_time("2024-04-01")
    def test_reconcile_grouped_payments_single_batch_by_default(self):
        self.inbound_mode.generate_move = True
        self.inbound_mode.post_move = True
        old_partner = self.partner
        self.partner = self.env["res.partner"].create({"name": "Test Partner 2"})
        invoice = self._create_customer_invoice()
        self.partner = old_partner
        invoice.action_post()
        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=invoice.ids
        ).create({}).run()
        self.inbound_order.draft2open()
        self.inbound_order.open2generated()

        original_reconcile = AccountMoveLine.reconcile
        with patch.object(
            AccountMoveLine,
            "reconcile",
            autospec=True,
            side_effect=original_reconcile,
        ) as reconcile_mock:
            self.inbound_order.generated2uploaded()

        # 2 payments, each reconciled once against its own invoice via
        # post_and_reconcile(), plus a single batch for the grouped move.
        self.assertEqual(reconcile_mock.call_count, 3)
