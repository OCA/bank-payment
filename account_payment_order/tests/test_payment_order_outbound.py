# © 2017 Camptocamp SA
# © 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, datetime, timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestPaymentOrderOutboundBase(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.company = cls.company_data["company"]
        cls.env.user.company_id = cls.company.id
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        cls.invoice_line_account = cls.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TEST1",
                "user_type_id": cls.env.ref("account.data_account_type_expenses").id,
            }
        )
        cls.mode = cls.env["account.payment.mode"].create(
            {
                "name": "Test Credit Transfer to Suppliers",
                "company_id": cls.company.id,
                "bank_account_link": "variable",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
            }
        )
        cls.creation_mode = cls.env["account.payment.mode"].create(
            {
                "name": "Test Direct Debit of suppliers from Société Générale",
                "company_id": cls.company.id,
                "bank_account_link": "variable",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
            }
        )
        cls.invoice = cls._create_supplier_invoice(cls, "F1242")
        cls.invoice_02 = cls._create_supplier_invoice(cls, "F1243")
        cls.bank_journal = cls.company_data["default_journal_bank"]
        # Make sure no other payment orders are in the DB
        cls.domain = [
            ("state", "=", "draft"),
            ("payment_type", "=", "outbound"),
            ("company_id", "=", cls.env.user.company_id.id),
        ]
        cls.env["account.payment.order"].search(cls.domain).unlink()

    def _create_supplier_invoice(self, ref):
        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "move_type": "in_invoice",
                "ref": ref,
                "payment_mode_id": self.mode.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    (
                        0,
                        None,
                        {
                            "product_id": self.env.ref("product.product_product_4").id,
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "name": "product that cost 100",
                            "account_id": self.invoice_line_account.id,
                        },
                    )
                ],
            }
        )

        return invoice


class TestPaymentOrderOutbound(TestPaymentOrderOutboundBase):
    def test_creation_due_date(self):
        self.mode.variable_journal_ids = self.bank_journal
        self.mode.group_lines = False
        self.order_creation("due")

    def test_creation_no_date(self):
        self.mode.group_lines = True
        self.creation_mode.write(
            {
                "group_lines": False,
                "bank_account_link": "fixed",
                "default_date_prefered": "due",
                "fixed_journal_id": self.bank_journal.id,
            }
        )
        self.mode.variable_journal_ids = self.bank_journal
        self.order_creation(False)

    def test_creation_fixed_date(self):
        self.mode.write(
            {
                "bank_account_link": "fixed",
                "default_date_prefered": "fixed",
                "fixed_journal_id": self.bank_journal.id,
            }
        )

        self.invoice_02.action_post()
        self.order_creation("fixed")

    def order_creation(self, date_prefered):
        # Open invoice
        self.invoice.action_post()
        order_vals = {
            "payment_type": "outbound",
            "payment_mode_id": self.creation_mode.id,
        }
        if date_prefered:
            order_vals["date_prefered"] = date_prefered
        order = self.env["account.payment.order"].create(order_vals)
        with self.assertRaises(UserError):
            order.draft2open()

        order.payment_mode_id = self.mode.id
        order.payment_mode_id_change()
        self.assertEqual(order.journal_id.id, self.bank_journal.id)

        self.assertEqual(len(order.payment_line_ids), 0)
        if date_prefered:
            self.assertEqual(order.date_prefered, date_prefered)
        with self.assertRaises(UserError):
            order.draft2open()
        line_create = (
            self.env["account.payment.line.create"]
            .with_context(active_model="account.payment.order", active_id=order.id)
            .create({"date_type": "move", "move_date": datetime.now()})
        )
        line_create.payment_mode = "any"
        line_create.move_line_filters_change()
        line_create.populate()
        line_create.create_payment_lines()
        line_created_due = (
            self.env["account.payment.line.create"]
            .with_context(active_model="account.payment.order", active_id=order.id)
            .create({"date_type": "due", "due_date": datetime.now()})
        )
        line_created_due.populate()
        line_created_due.create_payment_lines()
        self.assertGreater(len(order.payment_line_ids), 0)
        order.draft2open()
        order.open2generated()
        order.generated2uploaded()
        self.assertEqual(order.move_ids[0].date, order.bank_line_ids[0].date)
        self.assertEqual(order.state, "uploaded")

    def test_cancel_payment_order(self):
        # Open invoice
        self.invoice.action_post()
        # Add to payment order using the wizard
        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=self.invoice.ids
        ).create({}).run()

        payment_order = self.env["account.payment.order"].search(self.domain)
        self.assertEqual(len(payment_order), 1)

        payment_order.write({"journal_id": self.bank_journal.id})

        self.assertEqual(len(payment_order.payment_line_ids), 1)
        self.assertEqual(len(payment_order.bank_line_ids), 0)

        # Open payment order
        payment_order.draft2open()

        self.assertEqual(payment_order.bank_line_count, 1)

        # Generate and upload
        payment_order.open2generated()
        payment_order.generated2uploaded()

        self.assertEqual(payment_order.state, "uploaded")
        with self.assertRaises(UserError):
            payment_order.unlink()

        bank_line = payment_order.bank_line_ids

        with self.assertRaises(UserError):
            bank_line.unlink()
        payment_order.action_uploaded_cancel()
        self.assertEqual(payment_order.state, "cancel")
        payment_order.cancel2draft()
        payment_order.unlink()
        self.assertEqual(len(self.env["account.payment.order"].search(self.domain)), 0)

    def test_constrains(self):
        outbound_order = self.env["account.payment.order"].create(
            {
                "payment_type": "outbound",
                "payment_mode_id": self.mode.id,
                "journal_id": self.bank_journal.id,
            }
        )
        with self.assertRaises(ValidationError):
            outbound_order.date_scheduled = date.today() - timedelta(days=1)

    def test_manual_line_and_manual_date(self):
        # Create payment order
        outbound_order = self.env["account.payment.order"].create(
            {
                "date_prefered": "due",
                "payment_type": "outbound",
                "payment_mode_id": self.mode.id,
                "journal_id": self.bank_journal.id,
                "description": "order with manual line",
            }
        )
        self.assertEqual(len(outbound_order.payment_line_ids), 0)
        # Create a manual payment order line with custom date
        vals = {
            "order_id": outbound_order.id,
            "partner_id": self.partner.id,
            "communication": "manual line and manual date",
            "currency_id": outbound_order.payment_mode_id.company_id.currency_id.id,
            "amount_currency": 192.38,
            "date": date.today() + timedelta(days=8),
        }
        self.env["account.payment.line"].create(vals)
        self.assertEqual(len(outbound_order.payment_line_ids), 1)
        self.assertEqual(
            outbound_order.payment_line_ids[0].date, date.today() + timedelta(days=8)
        )
        # Create a manual payment order line with normal date
        vals = {
            "order_id": outbound_order.id,
            "partner_id": self.partner.id,
            "communication": "manual line",
            "currency_id": outbound_order.payment_mode_id.company_id.currency_id.id,
            "amount_currency": 200.38,
        }
        self.env["account.payment.line"].create(vals)
        self.assertEqual(len(outbound_order.payment_line_ids), 2)
        self.assertEqual(outbound_order.payment_line_ids[1].date, False)
        # Open payment order
        self.assertEqual(len(outbound_order.bank_line_ids), 0)
        outbound_order.draft2open()
        self.assertEqual(outbound_order.bank_line_count, 2)
        self.assertEqual(
            outbound_order.payment_line_ids[0].date,
            outbound_order.payment_line_ids[0].bank_line_id.date,
        )
        self.assertEqual(outbound_order.payment_line_ids[1].date, date.today())
        self.assertEqual(
            outbound_order.payment_line_ids[1].bank_line_id.date, date.today()
        )
