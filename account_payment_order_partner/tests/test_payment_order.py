# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import Form, TransactionCase


class TestPaymentOrderInboundBase(TransactionCase):
    def setUp(self):
        super(TestPaymentOrderInboundBase, self).setUp()
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
        self.journal = self.env["account.journal"].search(
            [("type", "=", "bank"), ("company_id", "=", self.env.user.company_id.id)],
            limit=1,
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
        self.inbound_order = (
            self.env["account.payment.order"]
            .with_context(is_pyo_as_per_customer=True)
            .create(
                {
                    "payment_type": "inbound",
                    "payment_mode_id": self.inbound_mode.id,
                    "journal_id": self.journal.id,
                    "state": "draft",
                }
            )
        )
        # Open invoice
        self.invoice = self._create_customer_invoice()
        self.invoice.action_post()

    def test_multi_link(self):
        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=self.invoice.ids
        ).create({}).run()

    def test_multi_new_link(self):
        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=self.invoice.ids
        ).create({}).run()

    def test_new_link(self):
        self.invoice = self._create_customer_invoice()
        self.invoice.action_post()
        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=self.invoice.ids
        ).create({}).create_new_orders()

    def test_new_link_without_paymentorder(self):
        self.invoice = self._create_customer_invoice()
        self.invoice.action_post()
        domain = [
            ("state", "=", "draft"),
            ("payment_type", "=", "inbound"),
            ("company_id", "=", self.env.user.company_id.id),
        ]
        self.payment_order_obj.search(domain).unlink()
        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=self.invoice.ids
        ).create({}).create_new_orders()

    def _create_customer_invoice(self):
        with Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
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
