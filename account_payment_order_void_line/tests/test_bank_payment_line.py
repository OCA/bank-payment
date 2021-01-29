# © 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, TransactionCase


class TestBankPayment(TransactionCase):
    def setUp(self):
        super(TestBankPayment, self).setUp()
        self.company = self.env.user.company_id
        self.journal = self.env["account.journal"].search(
            [("company_id", "=", self.company.id), ("type", "=", "purchase")], limit=1
        )
        self.partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        self.inbound_mode = self.env["account.payment.mode"].create(
            {
                "name": "Test Direct Debit of customers",
                "bank_account_link": "variable",
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
                "company_id": self.company.id,
            }
        )
        self.default_account_revenue = self.env["account.account"].search(
            [
                ("company_id", "=", self.company.id),
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_revenue").id,
                ),
            ],
            limit=1,
        )
        self.inbound_order = self.env["account.payment.order"].create(
            {
                "payment_type": "inbound",
                "payment_mode_id": self.inbound_mode.id,
                "journal_id": self.journal.id,
            }
        )
        self.invoice = self._create_customer_invoice()
        self.invoice.action_post()
        # Add to payment order using the wizard
        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=self.invoice.ids
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
                invoice_line_form.account_id = self.default_account_revenue
                invoice_line_form.tax_ids.clear()
        invoice = invoice_form.save()
        invoice_form = Form(invoice)
        invoice_form.payment_mode_id = self.inbound_mode
        return invoice_form.save()

    def test_bank_methods(self):
        payment_order = self.inbound_order
        self.assertEqual(len(payment_order.ids), 1)

        payment_order.write({"journal_id": self.journal.id})
        # Open payment order
        payment_order.draft2open()

        # Generate and upload
        payment_order.open2generated()
        payment_order.generated2uploaded()
        wizard = (
            self.env["cancel.void.payment.line"]
            .with_context(active_id=payment_order.bank_line_ids[0].id)
            .create({"reason": "No Reason"})
        )
        wizard.cancel_payment_line_entry()
