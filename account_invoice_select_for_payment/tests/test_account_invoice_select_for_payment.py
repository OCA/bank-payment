from odoo import fields
from odoo.tests import TransactionCase


class TestAccountMoveAndPayment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create common product and account for testing
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "list_price": 100}
        )
        cls.account = cls.env["account.account"].search(
            [("code", "=", "400000")], limit=1
        )

        # Create invoices for testing
        cls.invoice_1 = cls._create_invoice(
            partner_id=cls.env.ref("base.res_partner_1").id, selected_for_payment=False
        )
        cls.invoice_2 = cls._create_invoice(
            partner_id=cls.env.ref("base.res_partner_2").id, selected_for_payment=True
        )

    @classmethod
    def _create_invoice(cls, partner_id, selected_for_payment):
        invoice = cls.env["account.move"].create(
            {
                "invoice_date": fields.Date.today(),
                "move_type": "in_invoice",
                "partner_id": partner_id,
                "selected_for_payment": selected_for_payment,
            }
        )
        invoice.write(
            {
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "quantity": 1,
                            "price_unit": 100,
                            "account_id": cls.account.id,
                        },
                    )
                ]
            }
        )
        invoice.action_post()
        return invoice

    def test_action_toggle_select_for_payment(self):
        """Test toggling the 'selected_for_payment' status."""
        # Toggle selected_for_payment status for both invoices
        self.invoice_1.action_toggle_select_for_payment()
        self.invoice_2.action_toggle_select_for_payment()

        # Assert the expected results
        self.assertTrue(
            self.invoice_1.selected_for_payment,
            "Invoice 1 should be selected for payment.",
        )
        self.assertFalse(
            self.invoice_2.selected_for_payment,
            "Invoice 2 should not be selected for payment.",
        )

    def test_action_register_payment(self):
        """Test the 'action_register_payment' method with multiple invoices."""
        # Ensure initial selected_for_payment states
        self.assertFalse(self.invoice_1.selected_for_payment)
        self.assertTrue(self.invoice_2.selected_for_payment)

        self.invoice_1.action_register_payment()
        self.invoice_2.action_register_payment()

        # Validate that selected_for_payment is reset after payment
        self.env.invalidate_all()
        self.assertFalse(self.invoice_1.selected_for_payment)
        self.assertFalse(self.invoice_2.selected_for_payment)

    def test_register_payment_with_no_active_ids(self):
        """Test the 'action_register_payment' method when no active_ids are provided."""
        # Call register payment with no active_ids
        self.invoice_1.action_register_payment()

        # Ensure that no changes occurred to selected_for_payment
        self.env.invalidate_all()
        self.assertFalse(self.invoice_1.selected_for_payment)
        self.assertTrue(self.invoice_2.selected_for_payment)

    def test_to_pay_removal_when_paid(self):
        """Test that selected_for_payment is removed when invoice is fully paid"""
        # create and reconcile a payment without using the register payment wizard
        journal = self.env["account.journal"].search(
            [("type", "=", "bank"), ("company_id", "=", self.invoice_2.company_id.id)],
            limit=1,
        )
        payment = self.env["account.payment"].create(
            {
                "journal_id": journal.id,
                "amount": self.invoice_2.amount_total,
                "payment_type": "outbound",
                "partner_type": "supplier",
                "partner_id": self.invoice_2.partner_id.id,
            }
        )
        payment.action_post()
        _liquidity_line, payable_line, _write_off_line = payment._seek_for_lines()
        payable_invoice_line = self.invoice_2.line_ids.filtered(
            lambda line: line.account_id.account_type == "liability_payable"
        )
        self.assertTrue(self.invoice_2.selected_for_payment)
        (payable_line | payable_invoice_line).reconcile()
        self.assertFalse(self.invoice_2.selected_for_payment)
