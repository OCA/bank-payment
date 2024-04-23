# Copyright 2024 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo.exceptions import UserError
from odoo.tests import common, tagged


@tagged("-at_install", "post_install")
class TestAccountPaymentOrderLockDraft(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        """
        Set up necessary data for the test class.
        """
        super().setUpClass()
        # Date
        cls.date = date.today()
        # Product
        cls.product = cls.env.ref("product.product_product_7")
        # Partner
        cls.partner = cls.env.ref("base.res_partner_2")
        # Partner Bank
        cls.partner_bank = cls.env.ref("account_payment_mode.main_company_iban")
        # Payment Mode
        cls.payment_mode = cls.env.ref("account_payment_mode.payment_mode_outbound_ct1")
        # Invoice
        cls.invoice = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "invoice_date": cls.date,
                "move_type": "out_invoice",
                "payment_mode_id": cls.payment_mode.id,
                "partner_bank_id": cls.partner_bank.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "price_unit": 50.0,
                            "quantity": 1,
                        },
                    )
                ],
            }
        )

    def test_invoice_restriction(self):
        """
        Test if UserError is raised when trying to revert an invoice to draft
        status while it's associated with a Payment Order.
        """
        invoice = self.invoice
        # Confirm Invoice
        invoice.action_post()
        # Create Account Payment Line
        invoice.create_account_payment_line()
        # Check Invoice associated with a Payment Order
        with self.assertRaises(UserError):
            invoice.button_draft()
