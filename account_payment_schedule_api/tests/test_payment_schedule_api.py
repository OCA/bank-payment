# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta
from unittest.mock import patch

from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.account_payment_order_api.models.account_payment_api_batch import (
    PaymentApiResultUnknown,
)


class FakeBank:
    """Bank that accepts every line on sending and answers queries as told."""

    def __init__(self):
        self.send_answer = "accepted"
        self.query_answer = {}

    def reserve(self, batch):
        return f"LOT-{batch.id}"

    def send(self, batch):
        if isinstance(self.send_answer, Exception):
            raise self.send_answer
        return {
            "lines": {
                line.id: {"state": self.send_answer, "bank_reference": f"P{line.id}"}
                for line in batch.line_ids
            }
        }

    def query(self, batch):
        return {
            "lines": {
                line.id: self.query_answer.get(line.id) for line in batch.line_ids
            }
        }


@tagged("-at_install", "post_install")
class TestPaymentScheduleApi(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id |= cls.env.ref(
            "account_payment_order.group_account_payment"
        )
        cls.today = fields.Date.context_today(cls.env.user)
        mode_model = cls.env["account.payment.mode"]
        provider_field = mode_model._fields["api_provider"]
        cls.classPatch(provider_field, "selection", [("test", "Test Bank")])
        cls.classPatch(provider_field, "_selection", {"test": "Test Bank"})
        cls.mode = mode_model.create(
            {
                "name": "Test bank API",
                "company_id": cls.company_data["company"].id,
                "bank_account_link": "fixed",
                "fixed_journal_id": cls.company_data["default_journal_bank"].id,
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
                "api_provider": "test",
            }
        )

    def setUp(self):
        super().setUp()
        # The durable steps open their own cursor: share the test transaction.
        self.registry.enter_test_mode(self.cr)
        self.addCleanup(self.registry.leave_test_mode)
        self.bank = FakeBank()
        batch_class = type(self.env["account.payment.api.batch"])
        for operation in ("reserve", "send", "query"):
            patcher = patch.object(
                batch_class,
                f"_api_test_{operation}",
                create=True,
                new=lambda batch, *args, op=operation: getattr(self.bank, op)(
                    batch, *args
                ),
            )
            patcher.start()
            self.addCleanup(patcher.stop)
        self.items = self.env["account.move.line"]
        for amount in (100.0, 250.0):
            bill = self.env["account.move"].create(
                {
                    "move_type": "in_invoice",
                    "partner_id": self.partner_a.id,
                    "ref": f"BILL-{amount}",
                    "invoice_payment_term_id": False,
                    "invoice_date": self.today,
                    "invoice_date_due": self.today + timedelta(days=1),
                    "payment_mode_id": self.mode.id,
                    "invoice_line_ids": [
                        (0, 0, {"name": "Service", "price_unit": amount, "tax_ids": []})
                    ],
                }
            )
            bill.action_post()
            self.items |= bill.line_ids.filtered(
                lambda line: line.account_type == "liability_payable"
            )
        self.order = self.items._payment_schedule_create_orders()
        self.order.draft2open()

    def _api_line(self, item):
        return self.order.api_line_ids.filtered(lambda x: x.move_line_id == item)

    def _counters(self):
        data = self.env["account.move.line"].retrieve_payment_schedule_dashboard(
            [("partner_id", "=", self.partner_a.id)]
        )
        return {counter["filter"]: counter["count"] for counter in data["counters"]}

    def test_refused_item_comes_back_to_the_schedule(self):
        self.order.action_api_send()
        released, refused = self.items
        self.bank.query_answer = {
            self._api_line(released).id: {"state": "awaiting_release"},
            self._api_line(refused).id: {
                "state": "refused",
                "reason": "Invalid account",
            },
        }
        self.order.action_api_check()
        self.assertEqual(self.order.state, "open")
        self.assertEqual(released.payment_schedule_state, "in_progress")
        self.assertEqual(released.payment_schedule_bank_state, "awaiting_release")
        self.assertEqual(refused.payment_schedule_state, "to_schedule")
        self.assertEqual(refused.payment_schedule_bank_state, "refused")
        self.assertEqual(refused.payment_schedule_bank_reason, "Invalid account")
        move_lines = self.env["account.move.line"]
        self.assertEqual(
            move_lines.search(
                [
                    ("id", "in", self.items.ids),
                    ("payment_schedule_state", "=", "to_schedule"),
                ]
            ),
            refused,
        )
        self.assertEqual(
            move_lines.search(
                [
                    ("id", "in", self.items.ids),
                    ("payment_schedule_bank_state", "=", "awaiting_release"),
                ]
            ),
            released,
        )
        counters = self._counters()
        self.assertEqual(counters["bank_awaiting_release"], 1)
        self.assertEqual(counters["bank_refused"], 1)
        self.assertEqual(counters["bank_unknown"], 0)

        # Scheduled again, it leaves the refused counter.
        refused.payment_schedule_date = self.today + timedelta(days=2)
        refused._payment_schedule_create_orders()
        self.assertEqual(refused.payment_schedule_state, "draft_order")
        self.assertNotEqual(refused.payment_schedule_order_id, self.order)
        self.assertEqual(self._counters()["bank_refused"], 0)

    def test_unknown_outcome(self):
        self.bank.send_answer = PaymentApiResultUnknown("timeout")
        self.order.action_api_send()
        self.assertEqual(
            set(self.items.mapped("payment_schedule_bank_state")), {"unknown"}
        )
        self.assertEqual(
            set(self.items.mapped("payment_schedule_state")), {"in_progress"}
        )
        self.assertEqual(self._counters()["bank_unknown"], 2)
