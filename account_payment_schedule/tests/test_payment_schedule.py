# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT

from ..hooks import pre_init_hook


@tagged("-at_install", "post_install")
class TestPaymentSchedule(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.today = fields.Date.context_today(cls.env.user)
        cls.method = cls.env.ref("account.account_payment_method_manual_out")
        cls.mode = cls.env["account.payment.mode"].create(
            {
                "name": "Scheduled transfers",
                "company_id": cls.company_data["company"].id,
                "bank_account_link": "fixed",
                "fixed_journal_id": cls.company_data["default_journal_bank"].id,
                "payment_method_id": cls.method.id,
            }
        )

    def _payable(self, amount, days, mode=None):
        bill = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner_a.id,
                "ref": "BILL-%s" % amount,
                "invoice_payment_term_id": False,
                "invoice_date": self.today,
                "invoice_date_due": self.today + timedelta(days=days),
                "payment_mode_id": (mode if mode is not None else self.mode).id,
                "invoice_line_ids": [
                    (0, 0, {"name": "Service", "price_unit": amount, "tax_ids": []})
                ],
            }
        )
        bill.action_post()
        return bill.line_ids.filtered(
            lambda line: line.account_type == "liability_payable"
        )

    def _schedule(self, lines):
        action = lines.action_payment_schedule_create_orders()
        wizard = (
            self.env[action["res_model"]].with_context(**action["context"]).create({})
        )
        return wizard, wizard.action_create_orders()

    def test_scheduled_date_starts_as_due_date(self):
        line = self._payable(100.0, 3)
        self.assertEqual(line.payment_schedule_date, self.today + timedelta(days=3))
        self.assertEqual(line.payment_schedule_state, "to_schedule")
        line.payment_schedule_date = self.today + timedelta(days=1)
        self.assertEqual(line.payment_schedule_date, self.today + timedelta(days=1))
        self.assertFalse(line.payment_line_ids)

    def test_one_draft_order_per_mode_and_date(self):
        overdue = self._payable(100.0, -5)
        due_today = self._payable(200.0, 0)
        later = self._payable(300.0, 3) | self._payable(400.0, 3)
        self._schedule(overdue | due_today | later)
        today_order = overdue.payment_schedule_order_id
        self.assertEqual(today_order, due_today.payment_schedule_order_id)
        self.assertEqual(today_order.date_prefered, "fixed")
        self.assertEqual(today_order.date_scheduled, self.today)
        self.assertEqual(overdue.payment_schedule_date, self.today)
        self.assertTrue(today_order.description)
        later_order = later.payment_schedule_order_id
        self.assertEqual(len(later_order), 1)
        self.assertEqual(later_order.date_scheduled, self.today + timedelta(days=3))
        self.assertEqual(len(later_order.payment_line_ids), 2)
        self.assertEqual(
            set((overdue | due_today | later).mapped("payment_schedule_state")),
            {"draft_order"},
        )
        # A new item for the same date joins the draft order of that date.
        another = self._payable(50.0, 3)
        self._schedule(another)
        self.assertEqual(another.payment_schedule_order_id, later_order)

    def test_items_left_out(self):
        ready = self._payable(100.0, 1)
        no_mode = self._payable(200.0, 1, mode=self.env["account.payment.mode"])
        blocked = self._payable(250.0, 1)
        blocked.blocked = True
        taken = self._payable(300.0, 1)
        self._schedule(taken)
        self.assertEqual(no_mode.payment_schedule_state, "missing_instrument")
        self.assertEqual(blocked.payment_schedule_state, "blocked")
        wizard, _action = self._schedule(ready | no_mode | blocked | taken)
        self.assertEqual(wizard.ready_line_ids, ready)
        self.assertEqual(wizard.skipped_line_ids, no_mode | blocked | taken)
        self.assertEqual(wizard.ready_amount, 100.0)
        self.assertEqual(len(taken.payment_line_ids), 1)
        with self.assertRaises(UserError):
            self._schedule(no_mode)

    def test_bank_account_required(self):
        self.method.bank_account_required = True
        line = self._payable(100.0, 1)
        self.assertEqual(line.payment_schedule_state, "missing_instrument")
        line.partner_bank_id = self.env["res.partner.bank"].create(
            {"partner_id": self.partner_a.id, "acc_number": "123456"}
        )
        self.assertEqual(line.payment_schedule_state, "to_schedule")

    def test_new_date_moves_item_between_draft_orders(self):
        line = self._payable(100.0, 1)
        self._schedule(line)
        first_order = line.payment_schedule_order_id
        line.payment_schedule_date = self.today + timedelta(days=7)
        self.assertFalse(first_order.payment_line_ids)
        self.assertEqual(
            line.payment_schedule_order_id.date_scheduled,
            self.today + timedelta(days=7),
        )
        self.assertEqual(len(line.payment_line_ids), 1)

    def test_confirmed_order_keeps_its_date(self):
        line = self._payable(100.0, 1)
        self._schedule(line)
        order = line.payment_schedule_order_id
        order.draft2open()
        self.assertEqual(line.payment_schedule_state, "in_progress")
        with self.assertRaises(UserError):
            line.payment_schedule_date = self.today + timedelta(days=7)
        order.action_cancel()
        self.assertEqual(line.payment_schedule_state, "to_schedule")
        self.assertFalse(line.payment_schedule_order_id)

    def test_remove_from_order(self):
        line = self._payable(100.0, 1)
        self._schedule(line)
        order = line.payment_schedule_order_id
        line.action_payment_schedule_remove()
        self.assertEqual(line.payment_schedule_state, "to_schedule")
        self.assertFalse(order.payment_line_ids)

    def test_search_matches_status(self):
        lines = self._payable(100.0, 1)
        lines |= self._payable(200.0, 1, mode=self.env["account.payment.mode"])
        blocked = self._payable(250.0, 1)
        blocked.blocked = True
        scheduled = self._payable(300.0, 1)
        confirmed = self._payable(400.0, 2)
        self._schedule(scheduled | confirmed)
        confirmed.payment_schedule_order_id.draft2open()
        lines |= blocked | scheduled | confirmed
        move_lines = self.env["account.move.line"]
        for state in (
            "to_schedule",
            "missing_instrument",
            "blocked",
            "draft_order",
            "in_progress",
        ):
            found = move_lines.search(
                [("id", "in", lines.ids), ("payment_schedule_state", "=", state)]
            )
            self.assertEqual(
                found,
                lines.filtered(lambda line, s=state: line.payment_schedule_state == s),
                state,
            )
        others = move_lines.search(
            [("id", "in", lines.ids), ("payment_schedule_state", "!=", "draft_order")]
        )
        self.assertEqual(others, lines - scheduled)

    def test_pre_init_hook_fills_date(self):
        line = self._payable(100.0, 4)
        self.env.flush_all()
        self.cr.execute(
            "UPDATE account_move_line SET payment_schedule_date = NULL WHERE id = %s",
            (line.id,),
        )
        pre_init_hook(self.cr)
        line.invalidate_recordset(["payment_schedule_date"])
        self.assertEqual(line.payment_schedule_date, self.today + timedelta(days=4))

    def test_dashboard_counters(self):
        self._payable(100.0, -2)
        self._payable(200.0, 1, mode=self.env["account.payment.mode"])
        scheduled = self._payable(300.0, 4)
        self._schedule(scheduled)
        domain = [
            ("account_type", "=", "liability_payable"),
            ("parent_state", "=", "posted"),
            ("partner_id", "=", self.partner_a.id),
        ]
        data = self.env["account.move.line"].retrieve_payment_schedule_dashboard(domain)
        self.assertEqual(data["currency_id"], self.env.company.currency_id.id)
        counters = {counter["filter"]: counter for counter in data["counters"]}
        self.assertEqual(counters["to_schedule"]["count"], 1)
        self.assertEqual(counters["to_schedule"]["amount"], 100.0)
        self.assertEqual(counters["overdue"]["count"], 1)
        self.assertTrue(counters["overdue"]["alert"])
        self.assertEqual(counters["due_today"]["count"], 1)
        self.assertEqual(counters["missing_instrument"]["count"], 1)
        self.assertEqual(counters["draft_order"]["count"], 1)
        self.assertEqual(counters["draft_order"]["amount"], 300.0)
        self.assertEqual(counters["in_progress"]["count"], 0)
