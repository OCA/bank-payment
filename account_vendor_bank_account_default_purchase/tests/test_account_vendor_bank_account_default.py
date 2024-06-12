# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import odoo.tests

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@odoo.tests.tagged("post_install", "-at_install")
class TestAccountVendorBankAccountDefaultPurc(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.bank_account1 = cls.env["res.partner.bank"].create(
            {
                "acc_number": "12341",
                "partner_id": cls.partner_a.id,
            }
        )
        cls.bank_account2 = cls.env["res.partner.bank"].create(
            {
                "acc_number": "12342",
                "partner_id": cls.partner_a.id,
            }
        )
        cls.bank_account3 = cls.env["res.partner.bank"].create(
            {
                "acc_number": "12343",
                "partner_id": cls.partner_a.id,
            }
        )
        cls.product_a.type = "service"
        cls.manual_out = cls.env.ref("account.account_payment_method_manual_out")
        cls.journal_c1 = (
            cls.env["account.journal"]
            .sudo()
            .create({"name": "J1", "code": "J1", "type": "bank"})
        )
        cls.supplier_payment_mode = (
            cls.env["account.payment.mode"]
            .sudo()
            .create(
                {
                    "name": "Suppliers Bank 1",
                    "bank_account_link": "variable",
                    "payment_method_id": cls.manual_out.id,
                    "show_bank_account_from_journal": True,
                    "fixed_journal_id": cls.journal_c1.id,
                    "variable_journal_ids": [(6, 0, [cls.journal_c1.id])],
                }
            )
        )
        cls.partner_a.supplier_payment_mode_id = cls.supplier_payment_mode

    def create_purchase(self):
        return self.env["purchase.order"].create(
            {
                "partner_id": self.partner_a.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_a.id,
                            "name": self.product_a.name,
                            "product_qty": 1.0,
                        },
                    )
                ],
            }
        )

    def test_account_default_purchase(self):
        # Test the default partner account in purchase orders and its invoice
        self.partner_a.user_default_bank_id = self.bank_account2
        self.supplier_payment_mode.payment_method_id.bank_account_required = True
        purchase_id = self.create_purchase()
        self.assertEqual(purchase_id.supplier_partner_bank_id, self.bank_account2)
        purchase_id.button_confirm()
        invoice_id = (
            self.env["account.move"]
            .browse(purchase_id.action_create_invoice()["res_id"])
            .exists()
        )
        self.assertEqual(invoice_id.partner_bank_id, self.bank_account2)

    def test_no_account_default_purchase(self):
        # Test no bank account if bank_account is not required in payment mode
        self.partner_a.user_default_bank_id = self.bank_account2
        self.supplier_payment_mode.payment_method_id.bank_account_required = False
        purchase_id = self.create_purchase()
        self.assertFalse(purchase_id.supplier_partner_bank_id)

    def test_account_default_invoice_purchase(self):
        # Test the bank account propagation to invoices
        self.partner_a.user_default_bank_id = self.bank_account2
        self.supplier_payment_mode.payment_method_id.bank_account_required = True
        purchase_id = self.create_purchase()
        purchase_id.supplier_partner_bank_id = self.bank_account3
        purchase_id.button_confirm()
        invoice_id = (
            self.env["account.move"]
            .browse(purchase_id.action_create_invoice()["res_id"])
            .exists()
        )
        self.assertEqual(invoice_id.partner_bank_id, self.bank_account3)

    def test_no_payment_mode(self):
        # Test no bank account on purchases without payment mode
        self.partner_a.user_default_bank_id = self.bank_account2
        self.partner_a.supplier_payment_mode_id = False
        purchase_id = self.create_purchase()
        self.assertFalse(purchase_id.supplier_partner_bank_id)
