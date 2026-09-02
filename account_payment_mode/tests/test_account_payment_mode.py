# Copyright 2016-2020 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestAccountPaymentMode(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.res_users_model = cls.env["res.users"]
        cls.journal_model = cls.env["account.journal"]
        cls.payment_mode_model = cls.env["account.payment.mode"]

        # refs
        cls.manual_out = cls.env.ref("account.account_payment_method_manual_out")
        # Company
        cls.company = cls.env.ref("base.main_company")

        # Company 2
        cls.company_2 = cls.env["res.company"].create({"name": "Company 2"})

        cls.journal_c1 = cls._create_journal("J1", cls.company)
        cls.journal_c2 = cls._create_journal("J2", cls.company_2)
        cls.journal_c3 = cls._create_journal("J3", cls.company)

        cls.payment_mode_c1 = cls.payment_mode_model.create(
            {
                "name": "Direct Debit of suppliers from Bank 1",
                "bank_account_link": "variable",
                "payment_method_id": cls.manual_out.id,
                "company_id": cls.company.id,
                "fixed_journal_id": cls.journal_c1.id,
                "variable_journal_ids": [
                    (6, 0, [cls.journal_c1.id, cls.journal_c3.id])
                ],
            }
        )

    @classmethod
    def _create_journal(cls, name, company):
        # Create a cash account
        # Create a journal for cash account
        journal = cls.journal_model.create(
            {"name": name, "code": name, "type": "bank", "company_id": company.id}
        )
        return journal

    def test_payment_mode_company_consistency_change(self):
        # Assertion on the constraints to ensure the consistency
        # for company dependent fields
        with self.assertRaises(UserError):
            self.payment_mode_c1.write({"fixed_journal_id": self.journal_c2.id})
        with self.assertRaises(UserError):
            self.payment_mode_c1.write(
                {
                    "variable_journal_ids": [
                        Command.set(
                            [
                                self.journal_c1.id,
                                self.journal_c2.id,
                                self.journal_c3.id,
                            ],
                        )
                    ]
                }
            )
        with self.assertRaises(ValidationError):
            self.journal_c1.write({"company_id": self.company_2.id})

    def test_payment_mode_company_consistency_create(self):
        # Assertion on the constraints to ensure the consistency
        # for company dependent fields
        with self.assertRaises(UserError):
            self.payment_mode_model.create(
                {
                    "name": "Direct Debit of suppliers from Bank 2",
                    "bank_account_link": "variable",
                    "payment_method_id": self.manual_out.id,
                    "company_id": self.company.id,
                    "fixed_journal_id": self.journal_c2.id,
                }
            )

        with self.assertRaises(UserError):
            self.payment_mode_model.create(
                {
                    "name": "Direct Debit of suppliers from Bank 3",
                    "bank_account_link": "variable",
                    "payment_method_id": self.manual_out.id,
                    "company_id": self.company.id,
                    "variable_journal_ids": [(6, 0, [self.journal_c2.id])],
                }
            )

        with self.assertRaises(UserError):
            self.payment_mode_model.create(
                {
                    "name": "Direct Debit of suppliers from Bank 4",
                    "bank_account_link": "fixed",
                    "payment_method_id": self.manual_out.id,
                    "company_id": self.company.id,
                }
            )
        self.journal_c1.outbound_payment_method_line_ids = False
        with self.assertRaises(ValidationError):
            self.payment_mode_model.create(
                {
                    "name": "Direct Debit of suppliers from Bank 5",
                    "bank_account_link": "fixed",
                    "payment_method_id": self.manual_out.id,
                    "company_id": self.company.id,
                    "fixed_journal_id": self.journal_c1.id,
                }
            )
        self.journal_c1.inbound_payment_method_line_ids = False
        with self.assertRaises(ValidationError):
            self.payment_mode_model.create(
                {
                    "name": "Direct Debit of suppliers from Bank 5",
                    "bank_account_link": "fixed",
                    "payment_method_id": self.env.ref(
                        "account.account_payment_method_manual_in"
                    ).id,
                    "company_id": self.company.id,
                    "fixed_journal_id": self.journal_c1.id,
                }
            )

    def _create_payment_mode(self, name, company=None):
        return self.payment_mode_model.create(
            {
                "name": name,
                "bank_account_link": "variable",
                "payment_method_id": self.manual_out.id,
                "company_id": (company or self.company).id,
            }
        )

    def test_name_unique_same_company(self):
        self._create_payment_mode("Boleto")
        with self.assertRaises(ValidationError):
            self._create_payment_mode("Boleto")

    def test_name_unique_is_case_and_space_insensitive(self):
        self._create_payment_mode("Boleto")
        for duplicate in ("BOLETO", "boleto", " Boleto "):
            with self.assertRaises(ValidationError):
                self._create_payment_mode(duplicate)

    def test_name_unique_per_company(self):
        # The very same name is allowed in another company
        self._create_payment_mode("Boleto")
        mode = self._create_payment_mode("Boleto", company=self.company_2)
        self.assertEqual(mode.company_id, self.company_2)

    def test_name_unique_ignores_archived_modes(self):
        self._create_payment_mode("Boleto").action_archive()
        mode = self._create_payment_mode("Boleto")
        self.assertTrue(mode.active)

    def test_name_unique_on_unarchive(self):
        archived = self._create_payment_mode("Boleto")
        archived.action_archive()
        self._create_payment_mode("Boleto")
        with self.assertRaises(ValidationError):
            archived.action_unarchive()

    def test_name_unique_on_rename(self):
        self._create_payment_mode("Boleto")
        other = self._create_payment_mode("Pix")
        with self.assertRaises(ValidationError):
            other.write({"name": "Boleto"})

    def test_name_unique_within_same_batch(self):
        with self.assertRaises(ValidationError):
            self.payment_mode_model.create(
                [
                    {
                        "name": "Boleto",
                        "bank_account_link": "variable",
                        "payment_method_id": self.manual_out.id,
                        "company_id": self.company.id,
                    },
                    {
                        "name": "Boleto",
                        "bank_account_link": "variable",
                        "payment_method_id": self.manual_out.id,
                        "company_id": self.company.id,
                    },
                ]
            )

    def test_rename_keeping_own_name_is_allowed(self):
        # Writing the same name on an existing record must not self-conflict
        mode = self._create_payment_mode("Boleto")
        mode.write({"name": "Boleto"})
        self.assertEqual(mode.name, "Boleto")

    def test_copy_renames_the_duplicate(self):
        mode = self._create_payment_mode("Boleto")
        self.assertEqual(mode.copy().name, "Boleto (copy)")

    def test_copy_twice_keeps_finding_a_free_name(self):
        mode = self._create_payment_mode("Boleto")
        self.assertEqual(mode.copy().name, "Boleto (copy)")
        self.assertEqual(mode.copy().name, "Boleto (copy 2)")
        self.assertEqual(mode.copy().name, "Boleto (copy 3)")

    def test_copy_with_an_explicit_name_is_left_alone(self):
        mode = self._create_payment_mode("Boleto")
        self.assertEqual(mode.copy({"name": "Pix"}).name, "Pix")

    def test_copy_to_another_company_keeps_the_name(self):
        # The name is free in the target company, so there is nothing to avoid
        mode = self._create_payment_mode("Boleto")
        copy = mode.copy({"company_id": self.company_2.id})
        self.assertEqual(copy.name, "Boleto")
