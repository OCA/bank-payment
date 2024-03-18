# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo.tests.common import tagged

from odoo.addons.account_payment_order.tests.test_payment_order_outbound import (
    TestPaymentOrderOutboundBase,
)


@tagged("post_install", "-at_install")
class TestAccountPaymentInvoiceButton(TestPaymentOrderOutboundBase):
    def _create_payment_line(self, order):
        line_create = (
            self.env["account.payment.line.create"]
            .with_context(active_model="account.payment.order", active_id=order.id)
            .create(
                {"date_type": "move", "move_date": datetime.now() + timedelta(days=1)}
            )
        )
        line_create.payment_mode = "any"
        line_create.move_line_filters_change()
        line_create.populate()
        line_create.create_payment_lines()

    def test_supplier_invoice_payment_order_button(self):
        self.invoice.action_post()
        order_vals = {
            "payment_type": "outbound",
            "payment_mode_id": self.mode.id,
        }
        order = self.env["account.payment.order"].create(order_vals)
        order.payment_mode_id_change()
        self._create_payment_line(order)

        action = order.action_view_in_invoice()
        self.assertEqual(action["res_id"], self.invoice.id)

        self.invoice_02.action_post()
        self._create_payment_line(order)
        action = order.action_view_in_invoice()
        domain = action.get("domain")
        self.assertEqual(domain[0][0], "id")
        self.assertIn(self.invoice_02.id, domain[0][2])

    def test_customer_invoice_payment_order_button(self):
        sale_journal = self.env["account.journal"].search(
            [("type", "=", "sale"), ("company_id", "=", self.invoice.company_id.id)],
            limit=1,
        )
        (self.invoice | self.invoice_02).write(
            {"move_type": "out_refund", "journal_id": sale_journal.id}
        )
        self.invoice.action_post()
        order_vals = {
            "payment_type": "outbound",
            "payment_mode_id": self.mode.id,
        }
        order = self.env["account.payment.order"].create(order_vals)
        order.payment_mode_id_change()
        self._create_payment_line(order)

        action = order.action_view_out_invoice()
        self.assertEqual(action["res_id"], self.invoice.id)

        self.invoice_02.action_post()
        self._create_payment_line(order)
        action = order.action_view_out_invoice()
        domain = action.get("domain")
        self.assertEqual(domain[0][0], "id")
        self.assertIn(self.invoice_02.id, domain[0][2])
