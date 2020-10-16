# Copyright 2016-2020 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestAccountPaymentMode(TransactionCase):
    def setUp(self):
        super(TestAccountPaymentMode, self).setUp()
        self.res_users_model = self.env["res.users"]
        self.journal_model = self.env["account.journal"]
        self.payment_mode_model = self.env["account.payment.mode"]

        # refs
        self.manual_out = self.env.ref("account.account_payment_method_manual_out")
        # Company
        self.company = self.env.ref("base.main_company")

        # Company 2
        self.company_2 = self.env["res.company"].create({"name": "Company 2"})

        self.journal_c1 = self._create_journal("J1", self.company)
        self.journal_c2 = self._create_journal("J2", self.company_2)
        self.journal_c3 = self._create_journal("J3", self.company)

        self.payment_mode_c1 = self.payment_mode_model.create(
            {
                "name": "Direct Debit of suppliers from Bank 1",
                "bank_account_link": "variable",
                "payment_method_id": self.manual_out.id,
                "company_id": self.company.id,
                "fixed_journal_id": self.journal_c1.id,
                "variable_journal_ids": [
                    (6, 0, [self.journal_c1.id, self.journal_c3.id])
                ],
            }
        )

    def _create_journal(self, name, company):
        # Create a cash account
        # Create a journal for cash account
        journal = self.journal_model.create(
            {"name": name, "code": name, "type": "bank", "company_id": company.id}
        )
        return journal

    def test_payment_mode_company_consistency_change(self):
        # Assertion on the constraints to ensure the consistency
        # for company dependent fields
        with self.assertRaises(ValidationError):
            self.payment_mode_c1.write({"fixed_journal_id": self.journal_c2.id})
        with self.assertRaises(ValidationError):
            self.payment_mode_c1.write(
                {
                    "variable_journal_ids": [
                        (
                            6,
                            0,
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
        with self.assertRaises(ValidationError):
            self.payment_mode_model.create(
                {
                    "name": "Direct Debit of suppliers from Bank 2",
                    "bank_account_link": "variable",
                    "payment_method_id": self.manual_out.id,
                    "company_id": self.company.id,
                    "fixed_journal_id": self.journal_c2.id,
                }
            )

        with self.assertRaises(ValidationError):
            self.payment_mode_model.create(
                {
                    "name": "Direct Debit of suppliers from Bank 3",
                    "bank_account_link": "variable",
                    "payment_method_id": self.manual_out.id,
                    "company_id": self.company.id,
                    "variable_journal_ids": [(6, 0, [self.journal_c2.id])],
                }
            )

        with self.assertRaises(ValidationError):
            self.payment_mode_model.create(
                {
                    "name": "Direct Debit of suppliers from Bank 4",
                    "bank_account_link": "fixed",
                    "payment_method_id": self.manual_out.id,
                    "company_id": self.company.id,
                }
            )
        self.journal_c1.outbound_payment_method_ids = False
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
        self.journal_c1.inbound_payment_method_ids = False
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
