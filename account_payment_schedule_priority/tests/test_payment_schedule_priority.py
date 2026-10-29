# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.tests import tagged
from odoo.tools.misc import format_date

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("-at_install", "post_install")
class TestPaymentSchedulePriority(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id |= cls.env.ref(
            "account_payment_order.group_account_payment"
        )
        cls.today = fields.Date.context_today(cls.env.user)
        bank_journal = cls.company_data["default_journal_bank"]
        cls.mode = cls.env["account.payment.mode"].create(
            {
                "name": "Scheduled transfers",
                "company_id": cls.company_data["company"].id,
                "bank_account_link": "fixed",
                "fixed_journal_id": bank_journal.id,
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
            }
        )
        # 1000 in the bank today.
        entry = cls.env["account.move"].create(
            {
                "move_type": "entry",
                "date": cls.today,
                "journal_id": cls.company_data["default_journal_misc"].id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": bank_journal.default_account_id.id,
                            "debit": 1000.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": cls.company_data[
                                "default_account_revenue"
                            ].id,
                            "credit": 1000.0,
                        },
                    ),
                ],
            }
        )
        entry.action_post()

    def _day(self, days):
        return self.today + timedelta(days=days)

    def _item(self, move_type, amount, days, priority=None, partner=None):
        move = self.env["account.move"].create(
            {
                "move_type": move_type,
                "partner_id": (partner or self.partner_a).id,
                "ref": f"DOC-{amount}",
                "invoice_payment_term_id": False,
                "invoice_date": self.today,
                "invoice_date_due": self._day(days),
                "payment_mode_id": self.mode.id if move_type == "in_invoice" else False,
                "invoice_line_ids": [
                    (0, 0, {"name": "Service", "price_unit": amount, "tax_ids": []})
                ],
            }
        )
        move.action_post()
        line = move.line_ids.filtered(
            lambda line: line.account_type in ("asset_receivable", "liability_payable")
        )
        if priority:
            line.payment_priority = priority
        return line

    def _replan(self):
        move_lines = self.env["account.move.line"]
        action = move_lines.action_payment_schedule_replan()
        wizard = self.env[action["res_model"]].browse(action["res_id"])
        # Read the lines from the database, as the client does.
        wizard.invalidate_recordset()
        return wizard

    def test_priority_from_partner(self):
        self.partner_a.payment_priority = "2"
        self.assertEqual(self._item("in_invoice", 100.0, 1).payment_priority, "2")
        other = self._item("in_invoice", 100.0, 1, partner=self.partner_b)
        self.assertEqual(other.payment_priority, "3")

    def test_replan_order_and_apply(self):
        # 1400 to pay on day 2 with 1000 in the bank; 2000 comes in on day 10.
        critical = self._item("in_invoice", 700.0, 2, priority="1")
        low = self._item("in_invoice", 300.0, 2, priority="4")
        normal = self._item("in_invoice", 200.0, 2)
        normal_due_later = self._item("in_invoice", 200.0, 8)
        normal_due_later.payment_schedule_date = self._day(2)
        normal_due_later._payment_schedule_create_orders()
        self._item("out_invoice", 2000.0, 10)
        wizard = self._replan()
        self.assertEqual(
            wizard.move_ids.move_line_id.ids, [low.id, normal_due_later.id]
        )
        self.assertEqual(set(wizard.move_ids.mapped("new_date")), {self._day(10)})
        self.assertFalse(wizard.kept_ids)
        self.assertFalse(wizard.short_summary)
        plan = {line.move_line_id: line.new_date for line in wizard.move_ids}
        wizard.action_apply()
        for line, new_date in plan.items():
            self.assertEqual(line.payment_schedule_date, new_date)
        self.assertEqual(
            normal_due_later.payment_schedule_order_id.date_scheduled, self._day(10)
        )
        self.assertEqual(
            (critical | normal).mapped("payment_schedule_date"), [self._day(2)] * 2
        )
        move_lines = self.env["account.move.line"]
        cashflow = move_lines._get_payment_schedule_cashflow()
        self.assertFalse(move_lines._get_payment_schedule_short_dates(cashflow))

    def test_critical_and_confirmed_keep_their_date(self):
        critical = self._item("in_invoice", 1500.0, 2, priority="1")
        at_bank = self._item("in_invoice", 500.0, 3, priority="4")
        at_bank._payment_schedule_create_orders().draft2open()
        low = self._item("in_invoice", 100.0, 3, priority="4")
        self._item("out_invoice", 3000.0, 10)
        wizard = self._replan()
        self.assertEqual(wizard.move_ids.move_line_id, low)
        self.assertEqual(wizard.move_ids.new_date, self._day(10))
        # Moving everything that can move does not solve days 2 to 9.
        self.assertIn(format_date(self.env, self._day(9)), wizard.short_summary)
        wizard.action_apply()
        self.assertEqual(critical.payment_schedule_date, self._day(2))
        self.assertEqual(at_bank.payment_schedule_date, self._day(3))

    def test_no_later_date_keeps_items(self):
        low = self._item("in_invoice", 1500.0, 2, priority="4")
        wizard = self._replan()
        self.assertFalse(wizard.move_ids)
        self.assertEqual(wizard.kept_ids.move_line_id, low)
        self.assertTrue(wizard.short_summary)

    def test_nothing_short_nothing_moved(self):
        self._item("in_invoice", 300.0, 2, priority="4")
        wizard = self._replan()
        self.assertFalse(wizard.move_ids | wizard.kept_ids)
        self.assertFalse(wizard.short_summary)
