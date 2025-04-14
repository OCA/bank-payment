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
