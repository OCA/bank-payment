# Copyright 2017 Camptocamp SA
# Copyright 2017 Creu Blanca
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import Form, SavepointCase


class TestPaymentOrderInboundBase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        self = cls
        super().setUpClass()
        self.env.user.company_id = self.env.ref("base.main_company").id
        self.inbound_mode = self.env.ref(
            "account_payment_mode.payment_mode_inbound_dd1"
        )
        self.invoice_line_account = self.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TEST1",
                "user_type_id": self.env.ref("account.data_account_type_revenue").id,
            }
        )
        self.journal = self.env["account.journal"].create(
            {"name": "Test journal", "code": "BANK", "type": "bank"}
        )
        self.inbound_mode.variable_journal_ids = self.journal
        # Make sure no others orders are present
        self.domain = [
            ("state", "=", "draft"),
            ("payment_type", "=", "inbound"),
            ("company_id", "=", self.env.user.company_id.id),
        ]
        self.payment_order_obj = self.env["account.payment.order"]
        self.payment_order_obj.search(self.domain).unlink()
        # Create payment order
        self.inbound_order = self.env["account.payment.order"].create(
            {
                "payment_type": "inbound",
                "payment_mode_id": self.inbound_mode.id,
                "journal_id": self.journal.id,
            }
        )
        # Open invoice
        self.invoice = self._create_customer_invoice(self)
        self.invoice.action_post()
        # Add to payment order using the wizard
        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=self.invoice.ids
        ).create({}).run()

    def _create_customer_invoice(self):
        with Form(
            self.env["account.move"].with_context(default_type="out_invoice")
        ) as invoice_form:
            invoice_form.partner_id = self.env.ref("base.res_partner_4")
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

    def test_creation(self):
        payment_order = self.inbound_order
        self.assertEqual(len(payment_order.ids), 1)
        bank_journal = self.env["account.journal"].search(
            [("type", "=", "bank")], limit=1
        )
        # Set journal to allow cancelling entries
        bank_journal.update_posted = True

        payment_order.write({"journal_id": bank_journal.id})

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
        payment_order.action_done_cancel()
        self.assertEqual(payment_order.state, "cancel")
        payment_order.cancel2draft()
        payment_order.unlink()
        self.assertEqual(len(self.payment_order_obj.search(self.domain)), 0)
