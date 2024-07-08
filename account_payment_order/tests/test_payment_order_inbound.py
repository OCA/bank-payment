# Copyright 2017 Camptocamp SA
# Copyright 2017 Creu Blanca
# Copyright 2019-2022 Tecnativa - Pedro M. Baeza
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import date, timedelta

from freezegun import freeze_time

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import Form

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("-at_install", "post_install")
class TestPaymentOrderInboundBase(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        cls.company = cls.company_data["company"]
        cls.env.user.company_id = cls.company.id
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        cls.inbound_mode = cls.env["account.payment.mode"].create(
            {
                "name": "Test Direct Debit of customers",
                "bank_account_link": "variable",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
                "company_id": cls.company.id,
            }
        )
        cls.invoice_line_account = cls.company_data["default_account_revenue"]
        cls.journal = cls.company_data["default_journal_bank"]
        cls.inbound_mode.variable_journal_ids = cls.journal
        # Make sure no others orders are present
        cls.domain = [
            ("state", "=", "draft"),
            ("payment_type", "=", "inbound"),
            ("company_id", "=", cls.env.user.company_id.id),
        ]
        cls.payment_order_obj = cls.env["account.payment.order"]
        cls.payment_order_obj.search(cls.domain).unlink()
        # Create payment order
        cls.inbound_order = cls.env["account.payment.order"].create(
            {
                "payment_type": "inbound",
                "payment_mode_id": cls.inbound_mode.id,
                "journal_id": cls.journal.id,
            }
        )
        # Open invoice
        cls.invoice = cls._create_customer_invoice(cls)
        cls.invoice.action_post()
        # Add to payment order using the wizard
        cls.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=cls.invoice.ids
        ).create({}).run()

    def _create_customer_invoice(self):
        with Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        ) as invoice_form:
            invoice_form.partner_id = self.partner
            with invoice_form.invoice_line_ids.new() as invoice_line_form:
                invoice_line_form.product_id = self.env.ref("product.product_product_4")
                invoice_line_form.name = "product that cost 100"
                invoice_line_form.quantity = 1
                invoice_line_form.price_unit = 100.0
                invoice_line_form.account_id = self.invoice_line_account
                invoice_line_form.tax_ids.clear()
        invoice = invoice_form.save()
        invoice_form = Form(invoice)
        invoice_form.payment_mode_id = self.inbound_mode
        return invoice_form.save()


@tagged("-at_install", "post_install")
class TestPaymentOrderInbound(TestPaymentOrderInboundBase):
    def test_constrains_type(self):
        with self.assertRaises(ValidationError):
            order = self.env["account.payment.order"].create(
                {"payment_mode_id": self.inbound_mode.id, "journal_id": self.journal.id}
            )
            order.payment_type = "outbound"

    def test_constrains_date(self):
        with self.assertRaises(ValidationError):
            self.inbound_order.date_scheduled = date.today() - timedelta(days=1)

    def test_invoice_communication_01(self):
        self.assertEqual(
            self.invoice.name, self.invoice._get_payment_order_communication_direct()
        )
        self.invoice.ref = "R1234"
        self.assertEqual(
            self.invoice.name, self.invoice._get_payment_order_communication_direct()
        )

    def test_invoice_communication_02(self):
        self.invoice.payment_reference = "R1234"
        self.assertEqual(
            "R1234", self.invoice._get_payment_order_communication_direct()
        )

    def test_creation(self):
        payment_order = self.inbound_order
        self.assertEqual(len(payment_order.ids), 1)

        payment_order.write({"journal_id": self.journal.id})

        self.assertEqual(len(payment_order.payment_line_ids), 1)
        self.assertFalse(payment_order.payment_ids)

        # Open payment order
        payment_order.draft2open()

        self.assertEqual(payment_order.payment_count, 1)

        # Generate and upload
        payment_order.open2generated()
        payment_order.generated2uploaded()

        self.assertEqual(payment_order.state, "uploaded")
        with self.assertRaises(UserError):
            payment_order.unlink()
        matching_number = (
            payment_order.payment_ids.payment_line_ids.move_line_id.matching_number
        )
        self.assertTrue(matching_number and matching_number != "P")

        payment_order.action_uploaded_cancel()
        self.assertEqual(payment_order.state, "cancel")
        payment_order.cancel2draft()
        payment_order.unlink()
        self.assertEqual(len(self.payment_order_obj.search(self.domain)), 0)

    @freeze_time("2024-04-01")
    def test_creation_transfer_move_date_01(self):
        self.inbound_order.date_prefered = "fixed"
        self.inbound_order.date_scheduled = "2024-06-01"
        self.inbound_order.draft2open()
        payment = self.inbound_order.payment_ids
        self.assertEqual(payment.payment_line_date, date(2024, 6, 1))
        payment_move = payment.move_id
        self.assertEqual(payment_move.date, date(2024, 4, 1))  # now
        self.assertEqual(
            payment_move.line_ids.mapped("date_maturity"),
            [date(2024, 6, 1), date(2024, 6, 1)],
        )
        self.assertEqual(self.inbound_order.payment_count, 1)
        self.inbound_order.open2generated()
        self.inbound_order.generated2uploaded()
        self.assertEqual(self.inbound_order.state, "uploaded")
        payment = self.inbound_order.payment_ids
        self.assertEqual(payment.payment_line_date, date(2024, 6, 1))
        payment_move = payment.move_id
        self.assertEqual(payment_move.date, date(2024, 4, 1))  # now
        self.assertEqual(
            payment_move.line_ids.mapped("date_maturity"),
            [date(2024, 6, 1), date(2024, 6, 1)],
        )

    @freeze_time("2024-04-01")
    def test_creation_transfer_move_date_02(self):
        # Simulate that the invoice had a different due date
        self.inbound_order.payment_line_ids.ml_maturity_date = "2024-06-01"
        self.inbound_order.draft2open()
        payment = self.inbound_order.payment_ids
        self.assertEqual(payment.payment_line_date, date(2024, 6, 1))
        payment_move = payment.move_id
        self.assertEqual(payment_move.date, date(2024, 4, 1))  # now
        self.assertEqual(
            payment_move.line_ids.mapped("date_maturity"),
            [date(2024, 6, 1), date(2024, 6, 1)],
        )
        self.assertEqual(self.inbound_order.payment_count, 1)
        self.inbound_order.open2generated()
        self.inbound_order.generated2uploaded()
        self.assertEqual(self.inbound_order.state, "uploaded")
        payment = self.inbound_order.payment_ids
        self.assertEqual(payment.payment_line_date, date(2024, 6, 1))
        payment_move = payment.move_id
        self.assertEqual(payment_move.date, date(2024, 4, 1))  # now
        self.assertEqual(
            payment_move.line_ids.mapped("date_maturity"),
            [date(2024, 6, 1), date(2024, 6, 1)],
        )
