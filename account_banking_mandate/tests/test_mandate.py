# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import Command, fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestMandate(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.company_data["company"]
        cls.test_company = cls.setup_other_company(
            name="TEST Banking Mandate company",
        )
        cls.company_2 = cls.test_company["company"]
        cls.env.user.write(
            {
                "groups_id": [
                    Command.link(
                        cls.env.ref("account_payment_order.group_account_payment").id
                    )
                ],
                "company_ids": [
                    Command.link(cls.company_2.id),
                    Command.link(cls.company.id),
                ],
            }
        )
        cls.company_2.partner_id.company_id = cls.company_2.id
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test mandate partner",
                "company_id": cls.company.id,
            }
        )
        cls.bank_account = cls.env["res.partner.bank"].create(
            {
                "acc_number": "FR86 1234 5678 9012 1857 3900 A98",
                "partner_id": cls.partner.id,
                "company_id": cls.company.id,
            }
        )
        cls.mandate = cls.env["account.banking.mandate"].create(
            {
                "partner_bank_id": cls.bank_account.id,
                "signature_date": "2015-01-01",
                "company_id": cls.company.id,
            }
        )
        cls.other_partner = cls.env["res.partner"].create(
            {"name": "Other test partner"}
        )
        cls.other_bank_account = cls.env["res.partner.bank"].create(
            {
                "acc_number": "FR55 1234 5678 9012 2683 2930 A98",
                "partner_id": cls.partner.id,
            }
        )

    def test_mandate_01(self):
        self.assertEqual(self.mandate.state, "draft")
        self.mandate.validate()
        self.assertEqual(self.mandate.state, "valid")
        self.mandate.cancel()
        self.assertEqual(self.mandate.state, "cancel")
        self.mandate.back2draft()
        self.assertEqual(self.mandate.state, "draft")

    def test_mandate_02(self):
        with self.assertRaises(UserError):
            self.mandate.back2draft()

    def test_mandate_03(self):
        self.mandate.validate()
        with self.assertRaises(UserError):
            self.mandate.validate()

    def test_mandate_04(self):
        self.mandate.validate()
        self.mandate.cancel()
        with self.assertRaises(UserError):
            self.mandate.cancel()

    def test_onchange_methods(self):
        self.mandate.partner_bank_id = self.other_bank_account
        self.mandate.mandate_partner_bank_change()
        self.assertEqual(self.mandate.partner_id, self.other_bank_account.partner_id)

    def test_constrains_01(self):
        self.mandate.validate()
        with self.assertRaises(ValidationError):
            self.mandate.signature_date = fields.Date.to_string(
                fields.Date.from_string(fields.Date.context_today(self.mandate))
                + timedelta(days=1)
            )

    def test_constrains_02(self):
        with self.assertRaises(UserError):
            self.mandate.company_id = self.company_2

    def test_constrains_03(self):
        bank_account_2 = self.env["res.partner.bank"].create(
            {
                "acc_number": "FR74 1234 5678 9012 9308 8548 A98",
                "company_id": self.company_2.id,
                "partner_id": self.company_2.partner_id.id,
            }
        )
        with self.assertRaises(UserError):
            self.mandate.partner_bank_id = bank_account_2

    def test_constrains_04(self):
        mandate = self.env["account.banking.mandate"].create(
            {"signature_date": "2015-01-01", "company_id": self.company.id}
        )
        bank_account = self.env["res.partner.bank"].create(
            {
                "acc_number": "FR98 1234 5678 9012 8015 7721 A98",
                "company_id": self.company_2.id,
                "partner_id": self.company_2.partner_id.id,
            }
        )
        with self.assertRaises(UserError):
            bank_account.write({"mandate_ids": [Command.set(mandate.ids)]})

    def test_mandate_reference_01(self):
        """
        Test case: create a mandate with no reference
        Expected result: the reference of the created mandate is not empty
        """
        mandate = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": self.other_bank_account.id,
                "signature_date": "2015-01-01",
                "company_id": self.company.id,
            }
        )
        self.assertTrue(mandate.unique_mandate_reference)

    def test_mandate_reference_02(self):
        """
        Test case: create a mandate with "ref01" as reference
        Expected result: the reference of the created mandate is "ref01"
        """
        mandate = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": self.other_bank_account.id,
                "signature_date": "2015-01-01",
                "company_id": self.company.id,
                "unique_mandate_reference": "ref01",
            }
        )
        self.assertEqual(mandate.unique_mandate_reference, "ref01")

    def test_mandate_reference_03(self):
        """
        Test case: create a mandate with "TEST" as reference
        Expected result: the reference of the created mandate is "TEST"
        """
        mandate = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": self.other_bank_account.id,
                "signature_date": "2015-01-01",
                "company_id": self.company.id,
                "unique_mandate_reference": "TEST",
            }
        )
        self.assertTrue(mandate.unique_mandate_reference)
        self.assertEqual(mandate.unique_mandate_reference, "TEST")

    def test_mandate_reference_04(self):
        """
        Test case: create a mandate with "/" as reference
        Expected result: the reference of the created mandate is not "/"
        """
        mandate = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": self.other_bank_account.id,
                "signature_date": "2015-01-01",
                "company_id": self.company.id,
            }
        )
        self.assertTrue(mandate.unique_mandate_reference)
        self.assertNotEqual(mandate.unique_mandate_reference, "New")

    def test_mandate_reference_05(self):
        """
        Test case: create a mandate without reference
        Expected result: the reference of the created mandate is not empty
        """
        mandate = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": self.other_bank_account.id,
                "signature_date": "2015-01-01",
                "company_id": self.company.id,
            }
        )
        self.assertTrue(mandate.unique_mandate_reference)
