# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime

import odoo.tests

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@odoo.tests.tagged("post_install", "-at_install")
class TestAccountVendorBankAccountDefault(AccountTestInvoicingCommon):
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

    def create_in_invoice(self):
        return self.env["account.move"].create(
            {
                "partner_id": self.partner_a.id,
                "move_type": "in_invoice",
                "invoice_date": datetime.date.today(),
            }
        )

    def test_account_default_partner(self):
        # Test that the default partner account can be pertmanently changed manually
        self.assertNotEqual(self.partner_a.default_bank_id, self.bank_account2)
        self.partner_a.default_bank_id = self.bank_account2
        self.assertEqual(self.partner_a.default_bank_id, self.bank_account2)
        self.bank_account4 = self.env["res.partner.bank"].create(
            {
                "acc_number": "12344",
                "partner_id": self.partner_a.id,
            }
        )
        self.assertEqual(self.partner_a.default_bank_id, self.bank_account2)

    def test_account_default_in_invoice(self):
        # Test the default partner account in vendor bills
        self.partner_a.default_bank_id = self.bank_account2
        self.supplier_payment_mode.payment_method_id.bank_account_required = True
        in_invoice = self.create_in_invoice()
        self.assertEqual(in_invoice.partner_bank_id, self.bank_account2)

    def test_no_account_default_in_vendor(self):
        # Test no bank account on partner without default bank account
        self.partner_a.has_default_bank_id = False
        self.supplier_payment_mode.payment_method_id.bank_account_required = True
        in_invoice = self.create_in_invoice()
        self.assertFalse(in_invoice.partner_bank_id)

    def test_no_account_default_in_invoice(self):
        # Test no bank account on moves without bank_account_required in payment mode
        self.partner_a.default_bank_id = self.bank_account2
        self.supplier_payment_mode.payment_method_id.bank_account_required = False
        in_invoice = self.create_in_invoice()
        self.assertFalse(in_invoice.partner_bank_id)

    def test_no_payment_mode(self):
        # Test no bank account if bank_account is not required in payment mode
        self.partner_a.default_bank_id = self.bank_account2
        self.partner_a.supplier_payment_mode_id = False
        in_invoice = self.create_in_invoice()
        self.assertFalse(in_invoice.partner_bank_id)

    def test_commercial_fields(self):
        # Test the default partner account in vendor bills with individual partner
        # Test that the default partner account can be pertmanently changed manually
        self.partner_a.default_bank_id = self.bank_account2
        self.supplier_payment_mode.payment_method_id.bank_account_required = True
        in_invoice = self.create_in_invoice()
        self.assertEqual(in_invoice.partner_bank_id, self.bank_account2)
