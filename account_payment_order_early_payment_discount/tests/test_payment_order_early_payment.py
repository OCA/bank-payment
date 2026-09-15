# Copyright 2026 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import date

from freezegun import freeze_time

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestPaymentOrderEarlyPayment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        journal = cls.env["account.journal"].search([("type", "=", "bank")], limit=1)
        cls.mode = cls.env["account.payment.mode"].create(
            {
                "name": "Transfer",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
                "bank_account_link": "fixed",
                "fixed_journal_id": journal.id,
                "payment_order_ok": True,
            }
        )
        cls.supplier = cls.env["res.partner"].create(
            {
                "name": "Early Payer Supplier",
                "early_payment_percent": 2.0,
                "early_payment_percent_2": 1.0,
                "early_payment_days": 10,
                "early_payment_base": "invoice",
                "supplier_payment_mode_id": cls.mode.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Bolt", "type": "consu"}
        )
        cls.product.supplier_taxes_id = False

    def _bill(self, partner=None, invoice_date="2026-09-10"):
        bill = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": (partner or self.supplier).id,
                "invoice_date": invoice_date,
                "invoice_date_due": invoice_date,
                "ref": f"SUP-{invoice_date}",
                "payment_mode_id": self.mode.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "quantity": 10,
                            "price_unit": 100.0,
                        }
                    )
                ],
            }
        )
        bill.action_post()
        return bill

    def _order_on(self, date_scheduled):
        return self.env["account.payment.order"].create(
            {
                "payment_mode_id": self.mode.id,
                "payment_type": "outbound",
                "date_scheduled": date_scheduled,
            }
        )

    def _payable_lines(self, bill):
        return bill.line_ids.filtered(
            lambda line: line.account_id.account_type == "liability_payable"
        )

    @freeze_time("2026-09-15")
    def test_the_payment_order_proposes_the_discounted_amount(self):
        bill = self._bill()
        bill.create_account_payment_line()
        order = self.env["account.payment.order"].search(
            [("payment_mode_id", "=", self.mode.id)]
        )
        self.assertEqual(len(order.payment_line_ids), 1)
        self.assertAlmostEqual(order.payment_line_ids.amount_currency, 970.2)
        self.assertTrue(
            bill.early_payment_credit_note_id,
            "the discount is taken when the payment is proposed",
        )

    @freeze_time("2026-09-15")
    def test_a_late_payment_order_takes_no_discount(self):
        bill = self._bill(invoice_date="2026-01-10")
        bill.create_account_payment_line()
        order = self.env["account.payment.order"].search(
            [("payment_mode_id", "=", self.mode.id)]
        )
        self.assertAlmostEqual(order.payment_line_ids.amount_currency, 1000.0)
        self.assertFalse(bill.early_payment_credit_note_id)

    @freeze_time("2026-09-15")
    def test_a_preferred_supplier_stays_in_the_payment_order(self):
        self.supplier.preferred_supplier = True
        bill = self._bill()
        bill.create_account_payment_line()
        order = self.env["account.payment.order"].search(
            [("payment_mode_id", "=", self.mode.id)]
        )
        clerk = self.env["res.users"].create(
            {
                "name": "Clerk",
                "login": "payment_clerk",
                "group_ids": [
                    Command.link(self.env.ref("account.group_account_invoice").id),
                    Command.link(
                        self.env.ref("account_payment_order.group_account_payment").id
                    ),
                ],
            }
        )
        with self.assertRaises(UserError):
            order.payment_line_ids.with_user(clerk).unlink()
        manager = self.env["res.users"].create(
            {
                "name": "Manager",
                "login": "payment_manager",
                "group_ids": [
                    Command.link(self.env.ref("account.group_account_manager").id),
                    Command.link(
                        self.env.ref("account_payment_order.group_account_payment").id
                    ),
                ],
            }
        )
        order.payment_line_ids.with_user(manager).unlink()
        self.assertFalse(order.payment_line_ids, "the allowed group can")

    @freeze_time("2026-09-15")
    def test_a_preferred_supplier_comes_along_on_its_early_payment_date(self):
        """September 2026: the 30th is a Wednesday."""
        self.supplier.preferred_supplier = True
        bill = self._bill(invoice_date="2026-09-20")
        bill.invoice_date_due = date(2026, 10, 20)
        self.assertEqual(bill.early_payment_date, date(2026, 9, 30))
        plain = self.env["res.partner"].create(
            {"name": "Plain", "supplier_payment_mode_id": self.mode.id}
        )
        other = self._bill(partner=plain)

        order = self._order_on(date(2026, 9, 29))
        self._payable_lines(other).create_payment_line_from_move_line(order)
        order.draft2open()
        self.assertNotIn(
            bill,
            order.payment_line_ids.move_line_id.move_id,
            "the day before is not its day",
        )

        order = self._order_on(date(2026, 9, 30))
        order.draft2open()
        line = order.payment_line_ids
        self.assertEqual(
            line.move_line_id.move_id, bill, "thirty days of credit do not keep it out"
        )
        self.assertEqual(line.date, date(2026, 9, 30), "paid on the early payment date")
        self.assertAlmostEqual(line.amount_currency, 970.2, msg="net of the discount")
        self.assertTrue(bill.early_payment_credit_note_id)
        self.assertEqual(order.state, "open")

    @freeze_time("2026-09-15")
    def test_an_early_payment_on_a_weekend_is_paid_the_business_day_before(self):
        """September 26th 2026 is a Saturday: paid on Friday the 25th."""
        self.supplier.preferred_supplier = True
        bill = self._bill(invoice_date="2026-09-16")
        self.assertEqual(bill.early_payment_date, date(2026, 9, 26))
        order = self._order_on(date(2026, 9, 25))
        order.draft2open()
        self.assertEqual(order.payment_line_ids.move_line_id.move_id, bill)
        self.assertEqual(order.payment_line_ids.date, date(2026, 9, 25))

    @freeze_time("2026-09-15")
    def test_a_bill_of_a_plain_supplier_never_comes_along_by_itself(self):
        bill = self._bill(invoice_date="2026-09-20")
        with self.assertRaises(
            UserError, msg="nothing to pay: only preferred come along"
        ):
            self._order_on(date(2026, 9, 30)).draft2open()
        self.assertFalse(bill.early_payment_credit_note_id)
