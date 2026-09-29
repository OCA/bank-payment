# Copyright 2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

from freezegun import freeze_time

from odoo import fields
from odoo.tests.common import tagged

from odoo.addons.account_payment_order.tests.test_payment_order_outbound import (
    TestPaymentOrderOutboundBase,
)


@tagged("post_install", "-at_install")
class TestPaymentOrderOutbound(TestPaymentOrderOutboundBase):
    def test_grouped_output_uses_selected_payment_method_line(self):
        accounts = self.env["account.account"].create(
            [
                {
                    "name": "Outstanding payments A",
                    "code": "TESTOUTA",
                    "account_type": "liability_current",
                    "reconcile": True,
                },
                {
                    "name": "Outstanding payments B",
                    "code": "TESTOUTB",
                    "account_type": "liability_current",
                    "reconcile": True,
                },
            ]
        )
        method_lines = self.env["account.payment.method.line"].create(
            [
                {
                    "name": account.name,
                    "journal_id": self.bank_journal.id,
                    "payment_method_id": self.mode.payment_method_id.id,
                    "payment_account_id": account.id,
                }
                for account in accounts
            ]
        )
        order = self.env["account.payment.order"].create(
            {
                "payment_type": "outbound",
                "payment_mode_id": self.mode.id,
                "journal_id": self.bank_journal.id,
            }
        )
        payment = self.env["account.payment"].create(
            {
                "payment_type": "outbound",
                "partner_type": "supplier",
                "partner_id": self.partner.id,
                "journal_id": self.bank_journal.id,
                "payment_method_line_id": method_lines[0].id,
                "amount": 100.0,
            }
        )
        for method_line in method_lines:
            with self.subTest(payment_method_line=method_line.name):
                payment.payment_method_line_id = method_line
                self.assertEqual(
                    order._get_grouped_output_liquidity_account(payment),
                    method_line.payment_account_id,
                )

    @freeze_time("2024-04-01")
    def test_grouped_supplier_output(self):
        self.mode.generate_move = True
        self.mode.post_move = True
        self.order = self.env["account.payment.order"].create(
            {
                "date_prefered": "due",
                "payment_type": "outbound",
                "payment_mode_id": self.mode.id,
                "journal_id": self.bank_journal.id,
                "description": "order with manual line",
            }
        )
        vals = {
            "order_id": self.order.id,
            "partner_id": self.partner.id,
            "communication": "manual line and manual date",
            "currency_id": self.order.payment_mode_id.company_id.currency_id.id,
            "amount_currency": 192.38,
            "date": date.today() + timedelta(days=8),
        }
        self.env["account.payment.line"].create(vals)
        self.order.date_prefered = "fixed"
        self.order.date_scheduled = "2024-08-01"
        self.order.draft2open()
        payment = self.order.payment_ids
        payment_method_line = payment.payment_method_line_id
        payment_account = payment_method_line.payment_account_id
        payment_method_line.payment_account_id = False
        try:
            liquidity_account = self.order._get_grouped_output_liquidity_account(
                payment
            )
        finally:
            payment_method_line.payment_account_id = payment_account
        self.assertEqual(
            liquidity_account, payment._get_outstanding_account("outbound")
        )
        self.order.open2generated()
        self.order.generated2uploaded()
        grouped_moves = self.order.grouped_move_ids
        self.assertFalse(grouped_moves)
        # Add now a second line with different partner
        self.order.action_uploaded_cancel()
        self.order.cancel2draft()
        old_partner = self.partner
        self.partner = self.env["res.partner"].create({"name": "Test Partner 2"})
        invoice2 = self._create_supplier_invoice("test")
        self.partner = old_partner
        invoice2.action_post()
        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=invoice2.ids
        ).create({}).run()
        self.order.draft2open()
        self.order.open2generated()
        self.order.generated2uploaded()
        grouped_moves = self.order.grouped_move_ids
        self.assertTrue(grouped_moves)
        self.assertTrue(grouped_moves.line_ids[0].reconciled)
        self.assertTrue(
            all(
                x.date_maturity == fields.Date.from_string("2024-08-01")
                for x in grouped_moves.line_ids
            )
        )
        self.assertEqual(self.order.grouped_move_count, 1)
        self.order.action_uploaded_cancel()
        self.assertFalse(self.order.grouped_move_count)
