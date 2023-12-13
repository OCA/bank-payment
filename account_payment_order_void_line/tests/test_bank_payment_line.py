# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tests.common import Form

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("-at_install", "post_install")
class TestPaymentOrderInboundBase(AccountTestInvoicingCommon):
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
        cls.pay_method = cls.env["account.payment.method"].create(
            {"name": "default inbound", "code": "definb", "payment_type": "inbound"}
        )
        cls.journal = cls.company_data["default_journal_purchase"]
        cls.env['account.payment.method.line'].create({
            'name': "default inbound",
            'payment_type': "inbound",
            'journal_id': cls.journal.id,
            'payment_method_id': cls.pay_method.id,
        })
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
            .with_context(active_id=payment_order.payment_line_ids[0].id)
            .create({"reason": "No Reason"})
        )
        wizard.cancel_payment_line_entry()
