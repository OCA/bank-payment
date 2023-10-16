# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestMandate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        res = super(TestMandate, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.company = cls.env.ref("base.main_company")
        cls.company_2 = cls.env["res.company"].create({"name": "Company 2"})
        cls.company_2.partner_id.company_id = cls.company_2.id
        cls.bank_account = cls.env.ref("account_payment_mode.res_partner_12_iban")
        cls.bank_account.partner_id.company_id = cls.company.id
        cls.mandate = cls.env["account.banking.mandate"].create(
            {
                "partner_bank_id": cls.bank_account.id,
                "signature_date": "2015-01-01",
                "company_id": cls.company.id,
            }
        )
        return res

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
        bank_account_2 = self.env.ref("account_payment_mode.res_partner_2_iban")
        self.mandate.partner_bank_id = bank_account_2
        self.mandate.mandate_partner_bank_change()
        self.assertEqual(self.mandate.partner_id, bank_account_2.partner_id)

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
                "acc_number": "1234",
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
                "acc_number": "1234",
                "company_id": self.company_2.id,
                "partner_id": self.company_2.partner_id.id,
            }
        )
        with self.assertRaises(UserError):
            bank_account.write({"mandate_ids": [(6, 0, mandate.ids)]})

    def test_mandate_reference_01(self):
        """
        Test case: create a mandate with no reference
        Expected result: the reference of the created mandate is not empty
        """
        bank_account = self.env.ref("account_payment_mode.res_partner_12_iban")
        mandate = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": bank_account.id,
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
        bank_account = self.env.ref("account_payment_mode.res_partner_12_iban")
        mandate = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": bank_account.id,
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
        bank_account = self.env.ref("account_payment_mode.res_partner_12_iban")
        mandate = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": bank_account.id,
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
        bank_account = self.env.ref("account_payment_mode.res_partner_12_iban")
        mandate = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": bank_account.id,
                "signature_date": "2015-01-01",
                "company_id": self.company.id,
                "unique_mandate_reference": "/",
            }
        )
        self.assertTrue(mandate.unique_mandate_reference)
        self.assertNotEqual(mandate.unique_mandate_reference, "/")

    def test_mandate_reference_05(self):
        """
        Test case: create a mandate without reference
        Expected result: the reference of the created mandate is not empty
        """
        bank_account = self.env.ref("account_payment_mode.res_partner_12_iban")
        mandate = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": bank_account.id,
                "signature_date": "2015-01-01",
                "company_id": self.company.id,
            }
        )
        self.assertTrue(mandate.unique_mandate_reference)

    def test_mandate_reference_06(self):
        """
        Test case: create a mandate with False as reference (empty with UX)
        Expected result: the reference of the created mandate is not False
        """
        bank_account = self.env.ref("account_payment_mode.res_partner_12_iban")
        mandate_1 = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": bank_account.id,
                "signature_date": "2015-01-01",
                "company_id": self.company.id,
                "unique_mandate_reference": False,
            }
        )
        self.assertTrue(mandate_1.unique_mandate_reference)
        mandate_2 = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": bank_account.id,
                "signature_date": "2015-01-01",
                "company_id": self.company.id,
                "unique_mandate_reference": "",
            }
        )
        self.assertTrue(mandate_2.unique_mandate_reference)
