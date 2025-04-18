# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase, tagged

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@tagged("post_install", "-at_install")
class TestMandate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        res = super(TestMandate, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.company = cls.env.ref("base.main_company")
        if not cls.company.chart_template_id:
            # Load a CoA if there's none in the company
            coa = cls.env.ref("l10n_generic_coa.configurable_chart_template", False)
            if not coa:
                # Load the first available CoA
                coa = cls.env["account.chart.template"].search(
                    [("visible", "=", True)], limit=1
                )
            coa.try_loading(company=cls.company, install_demo=False)
        cls.company_2 = cls.env["res.company"].create({"name": "Company 2"})
        cls.company_2.partner_id.company_id = cls.company_2.id
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "company_id": cls.company.id,
            }
        )
        cls.bank = cls.env["res.bank"].create(
            {
                "name": "Fiducial Banque",
                "bic": "FIDCFR21XXX",
                "street": "38 rue Sergent Michel Berthet",
                "zip": "69009",
                "city": "Lyon",
                "country": cls.env.ref("base.fr").id,
            }
        )
        cls.bank_account = cls.env["res.partner.bank"].create(
            {
                "partner_id": cls.partner.id,
                "bank_id": cls.bank.id,
                "acc_number": "FR66 1212 1212 1212 1212 1212 121",
            }
        )
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
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner 2",
                "company_id": self.company.id,
            }
        )
        bank_account_2 = self.env["res.partner.bank"].create(
            {
                "partner_id": partner.id,
                "bank_id": self.bank.id,
                "acc_number": "FR66 1212 1212 1212 1212 1212 121",
            }
        )
        self.mandate.partner_bank_id = bank_account_2
        self.mandate.mandate_partner_bank_change()
        self.assertEqual(self.mandate.partner_id, partner)

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
        mandate = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": self.bank_account.id,
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
                "partner_bank_id": self.bank_account.id,
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
                "partner_bank_id": self.bank_account.id,
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
                "partner_bank_id": self.bank_account.id,
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
        mandate = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": self.bank_account.id,
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
        mandate_1 = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": self.bank_account.id,
                "signature_date": "2015-01-01",
                "company_id": self.company.id,
                "unique_mandate_reference": False,
            }
        )
        self.assertTrue(mandate_1.unique_mandate_reference)
        mandate_2 = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": self.bank_account.id,
                "signature_date": "2015-01-01",
                "company_id": self.company.id,
                "unique_mandate_reference": "",
            }
        )
        self.assertTrue(mandate_2.unique_mandate_reference)
