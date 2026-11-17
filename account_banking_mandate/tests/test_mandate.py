# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import tagged

from .common import AccountBankingMandateCommon


@tagged("post_install", "-at_install")
class TestMandate(AccountBankingMandateCommon):
    def test_01_mandate_lifecycle(self):
        self.assertEqual(self.mandate.state, "draft")
        self.mandate.validate()
        self.assertEqual(self.mandate.state, "valid")
        self.mandate.cancel()
        self.assertEqual(self.mandate.state, "cancel")
        self.mandate.back2draft()
        self.assertEqual(self.mandate.state, "draft")

    def test_02_back_to_draft_wrong_state(self):
        with self.assertRaises(UserError):
            self.mandate.back2draft()

    def test_03_validate_twice(self):
        self.mandate.validate()
        with self.assertRaises(UserError):
            self.mandate.validate()

    def test_04_cancel_twice(self):
        self.mandate.validate()
        self.mandate.cancel()
        with self.assertRaises(UserError):
            self.mandate.cancel()

    def test_05_onchange_partner(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner 2",
                "company_id": self.company.id,
            }
        )
        bank_account_2 = self._create_partner_bank(
            self.env, partner, "FR66 1212 1212 1212 1212 1212 121", self.company
        )
        self.mandate.partner_bank_id = bank_account_2
        self.mandate.mandate_partner_bank_change()
        self.assertEqual(self.mandate.partner_id, partner)

    def test_06_future_signature_date(self):
        self.mandate.validate()
        with self.assertRaises(ValidationError):
            self.mandate.signature_date = fields.Date.to_string(
                fields.Date.from_string(fields.Date.context_today(self.mandate))
                + timedelta(days=1)
            )

    def test_07_mandate_company_must_match_bank_account(self):
        with self.assertRaises(UserError):
            self.mandate.company_id = self.company_2

    def test_08_mandate_bank_account_company_must_match(self):
        with self.assertRaises(UserError):
            self.mandate.partner_bank_id = self.other_company_bank_account

    def test_09_bank_account_company_must_match_mandate(self):
        mandate = self.env["account.banking.mandate"].create(
            {"signature_date": "2015-01-01", "company_id": self.company.id}
        )
        with self.assertRaises(UserError):
            self.other_company_bank_account.write(
                {"mandate_ids": [(6, 0, mandate.ids)]}
            )

    def test_10_signature_date_is_required_to_validate(self):
        mandate = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": self.partner_bank.id,
                "company_id": self.company.id,
            }
        )
        with self.assertRaises(ValidationError):
            mandate.validate()

    def test_11_bank_account_is_required_to_validate(self):
        mandate = self.env["account.banking.mandate"].create(
            {"signature_date": "2015-01-01", "company_id": self.company.id}
        )
        with self.assertRaises(ValidationError):
            mandate.validate()

    def test_12_last_debit_cannot_precede_signature(self):
        with self.assertRaises(ValidationError):
            self.env["account.banking.mandate"].create(
                {
                    "partner_bank_id": self.partner_bank.id,
                    "signature_date": "2015-01-02",
                    "last_debit_date": "2015-01-01",
                    "company_id": self.company.id,
                }
            )

    def test_13_read_only_access_and_company_isolation(self):
        mandate_model = (
            self.env["account.banking.mandate"]
            .with_user(self.readonly_user)
            .with_context(allowed_company_ids=[self.company.id])
        )
        mandates = mandate_model.search([])
        self.assertIn(self.mandate.id, mandates.ids)
        self.assertNotIn(self.other_company_mandate.id, mandates.ids)
        with self.assertRaises(AccessError):
            mandate_model.create(
                {
                    "partner_bank_id": self.partner_bank.id,
                    "signature_date": "2015-01-01",
                    "company_id": self.company.id,
                }
            )
        with self.assertRaises(AccessError):
            mandate_model.browse(self.mandate.id).write({"state": "cancel"})

    def test_14_mandate_reference_is_generated(self):
        """
        Test case: create a mandate with no reference
        Expected result: the reference of the created mandate is not empty
        """
        mandate = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": self.partner_bank.id,
                "signature_date": "2015-01-01",
                "company_id": self.company.id,
            }
        )
        self.assertTrue(mandate.unique_mandate_reference)

    def test_15_mandate_reference_can_be_set(self):
        """
        Test case: create a mandate with "ref01" as reference
        Expected result: the reference of the created mandate is "ref01"
        """
        mandate = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": self.partner_bank.id,
                "signature_date": "2015-01-01",
                "company_id": self.company.id,
                "unique_mandate_reference": "ref01",
            }
        )
        self.assertEqual(mandate.unique_mandate_reference, "ref01")

    def test_16_mandate_reference_custom_value(self):
        """
        Test case: create a mandate with "TEST" as reference
        Expected result: the reference of the created mandate is "TEST"
        """
        mandate = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": self.partner_bank.id,
                "signature_date": "2015-01-01",
                "company_id": self.company.id,
                "unique_mandate_reference": "TEST",
            }
        )
        self.assertTrue(mandate.unique_mandate_reference)
        self.assertEqual(mandate.unique_mandate_reference, "TEST")

    def test_17_mandate_reference_slash_is_generated(self):
        """
        Test case: create a mandate with "/" as reference
        Expected result: the reference of the created mandate is not "/"
        """
        mandate = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": self.partner_bank.id,
                "signature_date": "2015-01-01",
                "company_id": self.company.id,
                "unique_mandate_reference": "/",
            }
        )
        self.assertTrue(mandate.unique_mandate_reference)
        self.assertNotEqual(mandate.unique_mandate_reference, "/")

    def test_18_mandate_reference_missing_is_generated(self):
        """
        Test case: create a mandate without reference
        Expected result: the reference of the created mandate is not empty
        """
        mandate = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": self.partner_bank.id,
                "signature_date": "2015-01-01",
                "company_id": self.company.id,
            }
        )
        self.assertTrue(mandate.unique_mandate_reference)

    def test_19_mandate_reference_false_or_empty_is_generated(self):
        """
        Test case: create a mandate with False as reference (empty with UX)
        Expected result: the reference of the created mandate is not False
        """
        mandate_1 = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": self.partner_bank.id,
                "signature_date": "2015-01-01",
                "company_id": self.company.id,
                "unique_mandate_reference": False,
            }
        )
        self.assertTrue(mandate_1.unique_mandate_reference)
        mandate_2 = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": self.partner_bank.id,
                "signature_date": "2015-01-01",
                "company_id": self.company.id,
                "unique_mandate_reference": "",
            }
        )
        self.assertTrue(mandate_2.unique_mandate_reference)
