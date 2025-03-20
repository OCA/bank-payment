# Copyright 2017 Camptocamp SA
# Copyright 2017 Creu Blanca
# Copyright 2019-2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

from odoo import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("-at_install", "post_install")
class TestPaymentOrderInboundBase(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.env.user.write(
            {
                "groups_id": [
                    Command.link(
                        cls.env.ref("account_payment_order.group_account_payment").id
                    )
                ]
            }
        )
        cls.company = cls.company_data["company"]
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        cls.payment_method_in = cls.env["account.payment.method"].create(
            {
                "name": "test inbound payment order ok",
                "code": "test_manual",
                "payment_type": "inbound",
                "payment_order_ok": True,
            }
        )
        cls.inbound_mode = cls.env["account.payment.method.line"].create(
            {
                "name": "Test Direct Debit of customers",
                "bank_account_link": "variable",
                "journal_id": cls.company_data["default_journal_bank"].id,
                "payment_method_id": cls.payment_method_in.id,
                "company_id": cls.company.id,
                "selectable": True,
            }
        )
        cls.journal = cls.company_data["default_journal_bank"]
        # Make sure no others orders are present
        cls.domain = [
            ("state", "=", "draft"),
            ("payment_type", "=", "inbound"),
            ("company_id", "=", cls.company.id),
        ]
        cls.payment_order_obj = cls.env["account.payment.order"]
        cls.payment_order_obj.search(cls.domain).unlink()
        # Create payment order
        cls.inbound_order = cls.env["account.payment.order"].create(
            {
                "payment_type": "inbound",
                "payment_method_line_id": cls.inbound_mode.id,
                "journal_id": cls.journal.id,
                "company_id": cls.company.id,
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
        line_vals = {
            "product_id": self.env.ref("product.product_product_4").id,
            "name": "product that cost 100",
            "quantity": 1,
            "account_id": self.company_data["default_account_revenue"].id,
            "price_unit": 100.0,
            "tax_ids": [Command.clear()],
        }
        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "move_type": "out_invoice",
                "company_id": self.company.id,
                "preferred_payment_method_line_id": self.inbound_mode.id,
                "invoice_line_ids": [Command.create(line_vals)],
            }
        )
        return invoice


@tagged("-at_install", "post_install")
class TestPaymentOrderInbound(TestPaymentOrderInboundBase):
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

        payment_order.action_uploaded_cancel()
        self.assertEqual(payment_order.state, "cancel")
        payment_order.cancel2draft()
        payment_order.unlink()
        self.assertEqual(len(self.payment_order_obj.search(self.domain)), 0)
