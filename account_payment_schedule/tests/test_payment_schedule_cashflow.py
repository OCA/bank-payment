# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@tagged("-at_install", "post_install")
class TestPaymentScheduleCashflow(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.today = fields.Date.context_today(cls.env.user)
        cls.bank_journal = cls.company_data["default_journal_bank"]
        cls.mode = cls.env["account.payment.mode"].create(
            {
                "name": "Scheduled transfers",
                "company_id": cls.company_data["company"].id,
                "bank_account_link": "fixed",
                "fixed_journal_id": cls.bank_journal.id,
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
            }
        )
        cls.move_lines = cls.env["account.move.line"]
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
                            "account_id": cls.bank_journal.default_account_id.id,
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

    def _item(self, move_type, amount, days):
        move = self.env["account.move"].create(
            {
                "move_type": move_type,
                "partner_id": self.partner_a.id,
                "ref": "DOC-%s" % amount,
                "invoice_payment_term_id": False,
                "invoice_date": self.today,
                "invoice_date_due": self.today + timedelta(days=days),
                "payment_mode_id": self.mode.id if move_type == "in_invoice" else False,
                "invoice_line_ids": [
                    (0, 0, {"name": "Service", "price_unit": amount, "tax_ids": []})
                ],
            }
        )
        move.action_post()
        return move.line_ids.filtered(
            lambda line: line.account_type in ("asset_receivable", "liability_payable")
        )

    def _day(self, cashflow, days):
        date = self.today + timedelta(days=days)
        return next(day for day in cashflow["days"] if day["date"] == date)

    def test_projected_balance(self):
        self._item("out_invoice", 500.0, -5)  # overdue, left out
        self._item("in_invoice", 300.0, -2)  # overdue payable, counts today
        self._item("out_invoice", 100.0, 2)
        scheduled = self._item("in_invoice", 900.0, 3)
        scheduled._payment_schedule_create_orders()
        cashflow = self.move_lines._get_payment_schedule_cashflow(days=10)
        self.assertEqual(cashflow["opening"], 1000.0)
        self.assertEqual(cashflow["overdue_receivable"], 500.0)
        self.assertEqual(self._day(cashflow, 0)["queue"], 300.0)
        self.assertEqual(self._day(cashflow, 0)["balance"], 700.0)
        self.assertEqual(self._day(cashflow, 2)["inflow"], 100.0)
        self.assertEqual(self._day(cashflow, 3)["draft"], 900.0)
        self.assertEqual(self._day(cashflow, 3)["balance"], -100.0)
        self.assertEqual(
            self.move_lines._get_payment_schedule_short_dates(cashflow),
            [self.today + timedelta(days=offset) for offset in range(3, 10)],
        )

    def test_short_of_cash(self):
        ok = self._item("in_invoice", 300.0, 1)
        short = self._item("in_invoice", 900.0, 3)
        found = self.move_lines.search(
            [
                ("id", "in", (ok | short).ids),
                ("payment_schedule_short_balance", "=", True),
            ]
        )
        self.assertEqual(found, short)
        self.assertTrue(short.payment_schedule_short_balance)
        self.assertFalse(ok.payment_schedule_short_balance)
        data = self.move_lines.retrieve_payment_schedule_dashboard(
            [("partner_id", "=", self.partner_a.id)]
        )
        counters = {counter["filter"]: counter["count"] for counter in data["counters"]}
        self.assertEqual(counters["short_balance"], 1)
        # A higher minimum balance turns the first date short too.
        self.env.company.payment_schedule_minimum_balance = 800.0
        ok.invalidate_recordset(["payment_schedule_short_balance"])
        self.assertTrue(ok.payment_schedule_short_balance)

    def test_warnings(self):
        self._item("in_invoice", 300.0, 1)
        short = self._item("in_invoice", 900.0, 3)
        self._item("out_invoice", 2000.0, 5)
        action = short.action_payment_schedule_create_orders()
        wizard = (
            self.env[action["res_model"]].with_context(**action["context"]).create({})
        )
        self.assertTrue(wizard.cash_warning)
        self.assertEqual(wizard.cash_warning.count("\n"), 1)  # date and recovery
        order = short._payment_schedule_create_orders()
        self.assertTrue(order.payment_schedule_cash_warning)
        self.env.company.payment_schedule_minimum_balance = -1000.0
        order.invalidate_recordset(["payment_schedule_cash_warning"])
        self.assertFalse(order.payment_schedule_cash_warning)

    def test_rpc_data_and_journal_filter(self):
        self._item("in_invoice", 300.0, 1)
        data = self.move_lines.retrieve_payment_schedule_cashflow()
        self.assertEqual(len(data["days"]), 30)
        self.assertIsInstance(data["days"][0]["date"], str)
        self.assertIn(self.bank_journal.id, [j["id"] for j in data["journals"]])
        self.assertEqual(data["days"][1]["outflow"], 300.0)
        other = self.env["account.journal"].create(
            {"name": "Other bank", "type": "bank", "code": "OTB"}
        )
        data = self.move_lines.retrieve_payment_schedule_cashflow(journal_id=other.id)
        self.assertEqual(data["journal_id"], other.id)
        self.assertEqual(data["days"][1]["outflow"], 0.0)
