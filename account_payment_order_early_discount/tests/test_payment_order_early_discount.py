# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# Dates 2026-10: 05 Mon, 09 Fri, 11 Sun, 12 Mon, 15 Thu, 17 Sat, 19 Mon
from datetime import date, datetime

from odoo import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tests import freeze_time, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestPaymentOrderEarlyDiscount(AccountTestInvoicingCommon):
    @classmethod
    def get_default_groups(cls):
        # Databases where new users do not get "Contact Creation" by default
        return (
            super().get_default_groups()
            | cls.env.ref("base.group_partner_manager")
            | cls.env.ref("account_payment_order.group_account_payment")
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.company_data["company"]
        Account = cls.env["account.account"]
        cls.discount_gain = Account.create(
            {"name": "Discount Gain", "code": "EPDGAIN", "account_type": "income_other"}
        )
        cls.discount_loss = Account.create(
            {"name": "Discount Loss", "code": "EPDLOSS", "account_type": "expense"}
        )
        company = cls.company
        company.account_journal_early_pay_discount_gain_account_id = cls.discount_gain
        company.account_journal_early_pay_discount_loss_account_id = cls.discount_loss
        cls.company.resource_calendar_id.tz = "UTC"
        cls.tax = cls.company_data["default_tax_purchase"].copy(
            {"name": "Purchase Tax 20%", "amount": 20.0}
        )
        cls.term = cls._term("included")
        cls.term_net = cls.env["account.payment.term"].create(
            {
                "name": "30 Days Net",
                "line_ids": [
                    Command.create(
                        {"value": "percent", "value_amount": 100, "nb_days": 30}
                    )
                ],
            }
        )
        cls.bank_journal = cls.company_data["default_journal_bank"]
        cls.mode = cls.env["account.payment.mode"].create(
            {
                "name": "Credit Transfer",
                "company_id": cls.company.id,
                "bank_account_link": "fixed",
                "fixed_journal_id": cls.bank_journal.id,
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
                "default_date_prefered": "due",
                "default_date_type": "due",
                "default_payment_mode": "any",
                "group_lines": True,
                "early_discount_pay_on_discount_date": True,
                "early_discount_extend_to_workday": True,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Supplier",
                "bank_ids": [
                    Command.create(
                        {
                            "acc_number": "AT611904300234573201",
                            "allow_out_payment": True,
                        }
                    )
                ],
            }
        )

    @classmethod
    def _term(cls, computation, percentage=2.0, days=10):
        return cls.env["account.payment.term"].create(
            {
                "name": f"{percentage}% {days} Days, 30 Days Net ({computation})",
                "early_discount": True,
                "discount_percentage": percentage,
                "discount_days": days,
                "early_pay_discount_computation": computation,
                "line_ids": [
                    Command.create(
                        {"value": "percent", "value_amount": 100, "nb_days": 30}
                    )
                ],
            }
        )

    def _bill(self, invoice_date, amount=1000.0, term=None, move_type="in_invoice"):
        bill = self.env["account.move"].create(
            {
                "move_type": move_type,
                "partner_id": self.partner.id,
                "ref": f"BILL-{self.env['account.move'].search_count([]) + 1}",
                "invoice_date": invoice_date,
                "invoice_payment_term_id": (term or self.term).id,
                "payment_mode_id": self.mode.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": "Service",
                            "quantity": 1,
                            "price_unit": amount,
                            "account_id": self.company_data[
                                "default_account_expense"
                            ].id,
                            "tax_ids": [Command.set(self.tax.ids)],
                        }
                    )
                ],
            }
        )
        if "check_total" in bill._fields:
            # account_invoice_check_total: verification total required when enabled
            bill.check_total = bill.amount_total
        bill.action_post()
        return bill

    def _order(self, date_prefered="due", **vals):
        return self.env["account.payment.order"].create(
            dict(
                {
                    "payment_type": "outbound",
                    "payment_mode_id": self.mode.id,
                    "date_prefered": date_prefered,
                },
                **vals,
            )
        )

    def _wizard(self, order, filter_date, **vals):
        return (
            self.env["account.payment.line.create"]
            .with_context(active_model="account.payment.order", active_id=order.id)
            .create(dict({"date_type": "due", "filter_date": filter_date}, **vals))
        )

    def _add(self, order, filter_date, **vals):
        wizard = self._wizard(order, filter_date, **vals)
        wizard.populate()
        wizard.create_payment_lines()
        return order.payment_line_ids

    def _found(self, wizard):
        return self.env["account.move.line"].search(wizard.move_line_domain).move_id

    @staticmethod
    def _term_line(bill):
        return bill.line_ids.filtered(lambda line: line.display_type == "payment_term")

    def _upload(self, order):
        order.draft2open()
        order.open2generated()
        order.generated2uploaded()

    def _discount_lines(self, payment):
        return payment.move_id.line_ids.filtered(
            lambda line: line.account_id == self.discount_gain or line.tax_line_id
        )

    def _assert_paid(self, *bills):
        for bill in bills:
            self.assertTrue(bill.currency_id.is_zero(bill.amount_residual), bill.name)
            self.assertIn(bill.payment_state, ("in_payment", "paid"), bill.name)

    def _assert_no_exchange_lines(self, payment):
        exchange_accounts = (
            self.company.income_currency_exchange_account_id
            | self.company.expense_currency_exchange_account_id
        )
        self.assertFalse(
            payment.move_id.line_ids.filtered(
                lambda line: line.account_id in exchange_accounts
            )
        )

    @freeze_time("2026-10-12")
    def test_wizard_selects_by_discount_date(self):
        bill = self._bill(date(2026, 10, 5))  # discount 10-15, net 11-04
        expired = self._bill(date(2026, 9, 20))  # discount 09-30, net 10-20
        order = self._order()
        wizard = self._wizard(order, date(2026, 10, 18))
        self.assertTrue(wizard.include_early_discount)
        self.assertIn(bill, self._found(wizard))
        self.assertNotIn(expired, self._found(wizard))
        wizard.include_early_discount = False
        self.assertNotIn(bill, self._found(wizard))
        wizard.include_early_discount = True
        wizard.due_on = "between"
        wizard.filter_date_end = date(2026, 10, 14)
        self.assertNotIn(bill, self._found(wizard))

    @freeze_time("2026-10-12")
    def test_discounted_amount_and_execution_date(self):
        bill = self._bill(date(2026, 10, 5))
        order = self._order()
        line = self._add(order, date(2026, 10, 18))
        self.assertEqual(line.move_line_id, self._term_line(bill))
        self.assertAlmostEqual(line.amount_currency, 1176.0)
        self.assertAlmostEqual(line.early_discount_amount, 24.0)
        self.assertEqual(line.ml_maturity_date, date(2026, 10, 15))
        order.draft2open()
        self.assertEqual(line.date, date(2026, 10, 15))
        payment = order.payment_ids
        self.assertAlmostEqual(payment.amount, 1176.0)
        order.open2generated()
        order.generated2uploaded()
        self._assert_paid(bill)
        lines = self._discount_lines(payment)
        self.assertAlmostEqual(sum(lines.mapped("balance")), -24.0)
        base = lines.filtered(lambda line: line.account_id == self.discount_gain)
        self.assertAlmostEqual(base.balance, -20.0)
        self.assertEqual(base.tax_ids, self.tax)
        self.assertAlmostEqual(lines.filtered("tax_line_id").balance, -4.0)
        self._assert_no_exchange_lines(payment)

    @freeze_time("2026-10-12")
    def test_same_entry_as_register_payment(self):
        def entry(move):
            return sorted(
                (
                    line.account_id.id,
                    round(line.balance, 2),
                    tuple(line.tax_ids.ids),
                    tuple(line.tax_tag_ids.ids),
                    line.tax_repartition_line_id.id,
                )
                for line in move.line_ids
            )

        method_line = self.bank_journal.outbound_payment_method_line_ids.filtered(
            lambda line: line.code == "manual"
        )[:1]
        for computation in ("included", "excluded", "mixed"):
            with self.subTest(computation=computation):
                term = self._term(computation)
                bill_wizard = self._bill(date(2026, 10, 5), term=term)
                bill_order = self._bill(date(2026, 10, 5), term=term)
                payment_wizard = (
                    self.env["account.payment.register"]
                    .with_context(
                        active_model="account.move", active_ids=bill_wizard.ids
                    )
                    .create(
                        {
                            "payment_date": date(2026, 10, 15),
                            "journal_id": self.bank_journal.id,
                            "payment_method_line_id": method_line.id,
                        }
                    )
                    ._create_payments()
                )
                order = self._order()
                order.payment_line_ids = [
                    Command.create(
                        self._term_line(bill_order)._prepare_payment_line_vals(order)
                    )
                ]
                self._upload(order)
                self._assert_paid(bill_wizard, bill_order)
                self.assertEqual(
                    entry(order.payment_ids.move_id), entry(payment_wizard.move_id)
                )
                self._assert_no_exchange_lines(order.payment_ids)

    @freeze_time("2026-10-12")
    def test_discount_period_ending_on_weekend(self):
        bill = self._bill(date(2026, 10, 1))  # discount Sun 10-11, net 10-31
        order = self._order()
        self.assertIn(bill, self._found(self._wizard(order, date(2026, 10, 12))))
        line = self._add(order, date(2026, 10, 12))
        self.assertAlmostEqual(line.amount_currency, 1176.0)
        self.assertEqual(line.ml_maturity_date, date(2026, 10, 12))
        self._upload(order)
        self.assertEqual(line.date, date(2026, 10, 12))
        self._assert_paid(bill)
        self.assertAlmostEqual(
            sum(self._discount_lines(order.payment_ids).mapped("balance")), -24.0
        )
        # Without the extension the discount period ended on Sunday
        self.mode.early_discount_extend_to_workday = False
        bill2 = self._bill(date(2026, 10, 1))
        order2 = self._order()
        self.assertNotIn(bill2, self._found(self._wizard(order2, date(2026, 10, 12))))
        vals = self._term_line(bill2)._prepare_payment_line_vals(order2)
        self.assertAlmostEqual(vals["amount_currency"], 1200.0)
        self.assertEqual(vals["early_discount_amount"], 0.0)

    def test_discount_deadline(self):
        mode = self.mode
        bill = self._bill(date(2026, 10, 5))  # discount Thu 10-15
        term_line = self._term_line(bill)
        currency = bill.currency_id
        mode.early_discount_extend_to_workday = False
        mode.early_discount_grace_days = 3
        self.assertEqual(
            term_line._get_payment_order_early_discount_deadline(mode),
            date(2026, 10, 18),
        )
        self.assertAlmostEqual(
            term_line._get_payment_order_early_discount(
                currency, date(2026, 10, 18), mode
            ),
            24.0,
        )
        self.assertEqual(
            term_line._get_payment_order_early_discount(
                currency, date(2026, 10, 19), mode
            ),
            0.0,
        )
        # Grace days ending on Sunday, extended to Monday
        mode.early_discount_extend_to_workday = True
        self.assertEqual(
            term_line._get_payment_order_early_discount_deadline(mode),
            date(2026, 10, 19),
        )
        # Without grace days: discount date is a working day
        mode.early_discount_grace_days = 0
        self.assertEqual(
            term_line._get_payment_order_early_discount_deadline(mode),
            date(2026, 10, 15),
        )
        # Discount on Saturday: planned on Monday (extended) or Friday
        sat_line = self._term_line(self._bill(date(2026, 10, 7)))
        self.assertEqual(sat_line.discount_date, date(2026, 10, 17))
        self.assertEqual(
            sat_line._get_payment_order_early_discount_date(mode), date(2026, 10, 19)
        )
        mode.early_discount_extend_to_workday = False
        self.assertEqual(
            sat_line._get_payment_order_early_discount_date(mode), date(2026, 10, 16)
        )

    @freeze_time("2026-10-12")
    def test_buffer_days_plan_payment_earlier(self):
        mode = self.mode
        mode.early_discount_buffer_days = 2
        bill = self._bill(date(2026, 10, 5))  # discount Thu 10-15
        term_line = self._term_line(bill)
        self.assertEqual(
            term_line._get_payment_order_early_discount_date(mode), date(2026, 10, 13)
        )
        # The buffer only plans earlier, the discount stays valid until 10-15
        self.assertEqual(
            term_line._get_payment_order_early_discount_deadline(mode),
            date(2026, 10, 15),
        )
        self.assertAlmostEqual(
            term_line._get_payment_order_early_discount(
                bill.currency_id, date(2026, 10, 15), mode
            ),
            24.0,
        )
        # Payment run on Monday 10-12: not selected with 2 days, with 3 days
        order = self._order()
        self.assertNotIn(bill, self._found(self._wizard(order, date(2026, 10, 12))))
        mode.early_discount_buffer_days = 3
        line = self._add(order, date(2026, 10, 12))
        self.assertEqual(line.ml_maturity_date, date(2026, 10, 12))
        self.assertAlmostEqual(line.amount_currency, 1176.0)
        self._upload(order)
        self.assertEqual(line.date, date(2026, 10, 12))
        self._assert_paid(bill)
        # Buffer ending on a weekend: planned on the working day before
        mode.early_discount_buffer_days = 2
        mon_line = self._term_line(self._bill(date(2026, 10, 9)))  # discount 10-19
        self.assertEqual(
            mon_line._get_payment_order_early_discount_date(mode), date(2026, 10, 16)
        )
        # Buffer and grace days together: planned earlier, discount valid longer
        mode.early_discount_grace_days = 3
        self.assertEqual(
            term_line._get_payment_order_early_discount_date(mode), date(2026, 10, 13)
        )
        self.assertEqual(
            term_line._get_payment_order_early_discount_deadline(mode),
            date(2026, 10, 19),
        )

    def test_negative_days_are_rejected(self):
        with self.assertRaises(ValidationError):
            self.mode.early_discount_grace_days = -1
        with self.assertRaises(ValidationError):
            self.mode.early_discount_buffer_days = -1

    def test_public_holiday_extends_deadline(self):
        self.env["resource.calendar.leaves"].create(
            {
                "name": "Feiertag",
                "calendar_id": self.company.resource_calendar_id.id,
                "date_from": datetime(2026, 10, 12, 0, 0),
                "date_to": datetime(2026, 10, 12, 23, 59, 59),
            }
        )
        term_line = self._term_line(self._bill(date(2026, 10, 1)))  # discount Sun
        self.assertEqual(
            term_line._get_payment_order_early_discount_deadline(self.mode),
            date(2026, 10, 13),
        )

    @freeze_time("2026-10-12")
    def test_discount_expired_at_confirmation(self):
        bill = self._bill(date(2026, 10, 5))
        order = self._order("now")
        line = self._add(order, date(2026, 10, 18))
        self.assertAlmostEqual(line.early_discount_amount, 24.0)
        order.write({"date_prefered": "fixed", "date_scheduled": date(2026, 10, 20)})
        messages = len(order.message_ids)
        order.draft2open()
        self.assertAlmostEqual(line.amount_currency, 1200.0)
        self.assertEqual(line.early_discount_amount, 0.0)
        self.assertGreater(len(order.message_ids), messages)
        self.assertIn(bill.name, order.message_ids[0].body)
        order.open2generated()
        order.generated2uploaded()
        self._assert_paid(bill)
        self.assertFalse(self._discount_lines(order.payment_ids))

    @freeze_time("2026-10-12")
    def test_due_date_without_option(self):
        self.mode.early_discount_pay_on_discount_date = False
        bill = self._bill(date(2026, 10, 5))
        order = self._order()
        line = self._add(order, date(2026, 11, 5))
        self.assertEqual(line.move_line_id.move_id, bill)
        self.assertEqual(line.ml_maturity_date, date(2026, 11, 4))
        self.assertAlmostEqual(line.amount_currency, 1200.0)
        self._upload(order)
        self.assertEqual(line.date, date(2026, 11, 4))
        self._assert_paid(bill)
        self.assertFalse(self._discount_lines(order.payment_ids))

    @freeze_time("2026-10-12")
    def test_bill_without_early_discount(self):
        bill = self._bill(date(2026, 10, 5), term=self.term_net)
        order = self._order()
        line = self._add(order, date(2026, 11, 5))
        self.assertAlmostEqual(line.amount_currency, 1200.0)
        self.assertEqual(line.early_discount_amount, 0.0)
        self.assertEqual(line.ml_maturity_date, date(2026, 11, 4))
        self._upload(order)
        self._assert_paid(bill)
        self.assertEqual(len(order.payment_ids.move_id.line_ids), 2)

    def _assert_discount_booked(self, payment, base, tax):
        lines = self._discount_lines(payment)
        self.assertAlmostEqual(
            sum(
                lines.filtered(
                    lambda line: line.account_id == self.discount_gain
                ).mapped("balance")
            ),
            base,
        )
        self.assertAlmostEqual(
            sum(lines.filtered("tax_line_id").mapped("balance")), tax
        )
        self.assertFalse(
            payment.move_id.line_ids.filtered(
                lambda line: line.account_id == self.discount_loss
            )
        )
        self._assert_no_exchange_lines(payment)

    @freeze_time("2026-10-12")
    def test_partial_payment_keeps_proportional_discount(self):
        # 100 paid without discount: 2 % of 100 is gone, 22 of 24 remain
        bill = self._bill(date(2026, 10, 5))
        self.env["account.payment.register"].with_context(
            active_model="account.move", active_ids=bill.ids
        ).create(
            {"amount": 100.0, "payment_date": date(2026, 10, 12)}
        )._create_payments()
        order = self._order("now")
        line = self._add(order, date(2026, 11, 5))
        self.assertAlmostEqual(line.early_discount_amount, 22.0)
        self.assertAlmostEqual(line.amount_currency, 1078.0)
        self._upload(order)
        self._assert_paid(bill)
        self._assert_discount_booked(order.payment_ids, -18.33, -3.67)

    @freeze_time("2026-10-12")
    def test_credit_note_with_discount_settled_before(self):
        # Credit note 120 shows 2.40 discount: only 117.60 reduce the payment
        bill = self._bill(date(2026, 10, 5))
        refund = self._bill(date(2026, 10, 6), amount=100.0, move_type="in_refund")
        (self._term_line(bill) | self._term_line(refund)).reconcile()
        self.assertAlmostEqual(bill.amount_residual, 1080.0)
        order = self._order()
        line = self._add(order, date(2026, 10, 18))
        self.assertEqual(line.ml_maturity_date, date(2026, 10, 15))
        self.assertAlmostEqual(line.early_discount_amount, 21.6)
        self.assertAlmostEqual(line.amount_currency, 1058.4)
        self._upload(order)
        self._assert_paid(bill, refund)
        self._assert_discount_booked(order.payment_ids, -18.0, -3.6)

    @freeze_time("2026-10-12")
    def test_credit_note_without_discount_settled_before(self):
        bill = self._bill(date(2026, 10, 5))
        refund = self._bill(
            date(2026, 10, 6), amount=100.0, term=self.term_net, move_type="in_refund"
        )
        (self._term_line(bill) | self._term_line(refund)).reconcile()
        order = self._order()
        line = self._add(order, date(2026, 10, 18))
        self.assertAlmostEqual(line.early_discount_amount, 24.0)
        self.assertAlmostEqual(line.amount_currency, 1056.0)
        self._upload(order)
        self._assert_paid(bill, refund)
        self._assert_discount_booked(order.payment_ids, -20.0, -4.0)

    @freeze_time("2026-10-12")
    def test_credit_note_with_discount_in_same_payment(self):
        bill = self._bill(date(2026, 10, 5))
        refund = self._bill(date(2026, 10, 6), amount=100.0, move_type="in_refund")
        order = self._order("now")
        self._add(order, date(2026, 10, 18))
        order.payment_line_ids = [
            Command.create(self._term_line(refund)._prepare_payment_line_vals(order))
        ]
        refund_line = order.payment_line_ids.filtered(
            lambda line: line.move_line_id.move_id == refund
        )
        self.assertAlmostEqual(refund_line.amount_currency, -117.6)
        self.assertAlmostEqual(refund_line.early_discount_amount, 2.4)
        self._upload(order)
        payment = order.payment_ids
        self.assertEqual(len(payment), 1)
        self.assertAlmostEqual(payment.amount, 1058.4)
        self._assert_paid(bill, refund)
        # Invoice -20/-4, credit note +2/+0.40 back on the discount gain account
        self._assert_discount_booked(payment, -18.0, -3.6)

    @freeze_time("2026-10-12")
    def test_manually_changed_amount_is_kept(self):
        bill = self._bill(date(2026, 10, 5))
        order = self._order()
        line = self._add(order, date(2026, 10, 18))
        line.amount_currency = 500.0
        self._upload(order)
        self.assertAlmostEqual(line.amount_currency, 500.0)
        self.assertEqual(line.early_discount_amount, 0.0)
        self.assertFalse(self._discount_lines(order.payment_ids))
        self.assertAlmostEqual(bill.amount_residual, 700.0)

    @freeze_time("2026-10-12")
    def test_grouped_payment_with_refund(self):
        bill = self._bill(date(2026, 10, 5))
        bill_net = self._bill(date(2026, 10, 5), term=self.term_net)
        refund = self._bill(
            date(2026, 10, 5), amount=100.0, term=self.term_net, move_type="in_refund"
        )
        order = self._order("now")
        self._add(order, date(2026, 11, 30))
        # Supplier refunds are added by hand (the wizard only proposes credit lines)
        order.payment_line_ids = [
            Command.create(self._term_line(refund)._prepare_payment_line_vals(order))
        ]
        lines = order.payment_line_ids
        self.assertEqual(len(lines), 3)
        self.assertAlmostEqual(sum(lines.mapped("amount_currency")), 2256.0)
        self._upload(order)
        payment = order.payment_ids
        self.assertEqual(len(payment), 1)
        self.assertAlmostEqual(payment.amount, 2256.0)
        self._assert_paid(bill, bill_net, refund)
        self.assertAlmostEqual(
            sum(self._discount_lines(payment).mapped("balance")), -24.0
        )
        self._assert_no_exchange_lines(payment)

    @freeze_time("2026-10-12")
    def test_paid_in_the_meantime_blocks_upload(self):
        bill = self._bill(date(2026, 10, 5))
        order = self._order()
        self._add(order, date(2026, 10, 18))
        order.draft2open()
        order.open2generated()
        self.env["account.payment.register"].with_context(
            active_model="account.move", active_ids=bill.ids
        ).create(
            {"amount": 100.0, "payment_date": date(2026, 10, 12)}
        )._create_payments()
        with self.assertRaises(UserError):
            order.generated2uploaded()

    @freeze_time("2026-10-12")
    def test_onchange_has_no_side_effects(self):
        bill = self._bill(date(2026, 10, 5))
        order = self._order()
        moves = self.env["account.move"].search_count([])
        line = self.env["account.payment.line"].new({"order_id": order.id})
        line.move_line_id = self._term_line(bill)
        line.move_line_id_change()
        self.assertAlmostEqual(line.amount_currency, 1176.0)
        self.assertAlmostEqual(line.early_discount_amount, 24.0)
        self.assertEqual(self.env["account.move"].search_count([]), moves)

    @freeze_time("2026-10-12")
    def test_confirm_again_after_cancel(self):
        bill = self._bill(date(2026, 10, 5))
        order = self._order()
        self._add(order, date(2026, 10, 18))
        order.draft2open()
        order.action_cancel()
        order.cancel2draft()
        self._upload(order)
        self.assertEqual(len(order.payment_ids), 1)
        self._assert_paid(bill)
        self.assertAlmostEqual(
            sum(self._discount_lines(order.payment_ids).mapped("balance")), -24.0
        )

    @freeze_time("2026-10-12")
    def test_missing_discount_accounts_block_upload(self):
        self._bill(date(2026, 10, 5))
        order = self._order()
        self._add(order, date(2026, 10, 18))
        order.draft2open()
        order.open2generated()
        self.company.account_journal_early_pay_discount_gain_account_id = False
        with self.assertRaisesRegex(UserError, "discount"):
            order.generated2uploaded()

    @freeze_time("2026-10-12")
    def test_other_discount_rates(self):
        # rates other than 2 %: 3 % / 7 days and 1.5 % / 14 days
        for percentage, days, discount, base, tax in (
            (3.0, 7, 36.0, -30.0, -6.0),
            (1.5, 14, 18.0, -15.0, -3.0),
        ):
            with self.subTest(percentage=percentage):
                bill = self._bill(
                    date(2026, 10, 9), term=self._term("included", percentage, days)
                )
                line_date = self._term_line(bill).discount_date
                order = self._order()
                line = self._add(order, line_date)
                self.assertEqual(line.ml_maturity_date, line_date)
                self.assertAlmostEqual(line.early_discount_amount, discount)
                self.assertAlmostEqual(line.amount_currency, 1200.0 - discount)
                self._upload(order)
                self._assert_paid(bill)
                self._assert_discount_booked(order.payment_ids, base, tax)
