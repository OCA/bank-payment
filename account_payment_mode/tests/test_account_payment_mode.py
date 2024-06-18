# Copyright 2016-2020 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestAccountPaymentMode(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

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

    def test_electronic_payment_methods_proposed_once(self):
        """Test that we cannot assign the same payment method when it's electronic
        to two journals of the same company."""
        method = (
            self.env["account.payment.method"]
            .sudo()
            .create(
                {
                    "name": "Electornic method",
                    "code": "electronic_method",
                    "payment_type": "inbound",
                }
            )
        )
        # We call with context variable electronic_code because by default because
        # we want to force that this payment method is considered electronic during testing,
        # even when it's not. The electronic mode is defaulted in the account_payment
        # module, but the restrictions for this mode live in the account module.
        journal_model = self.journal_model.with_context(
            electronic_code="electronic_method"
        )
        journal_c1_1 = journal_model.create(
            {
                "name": "J1_1",
                "code": "J1_1",
                "type": "bank",
                "company_id": self.company.id,
            }
        )
        self.assertIn(
            method,
            journal_c1_1.inbound_payment_method_line_ids.mapped("payment_method_id"),
        )
        journal_c1_2 = journal_model.create(
            {
                "name": "J1_2",
                "code": "J1_2",
                "type": "bank",
                "company_id": self.company.id,
            }
        )
        self.assertNotIn(
            method,
            journal_c1_2.inbound_payment_method_line_ids.mapped("payment_method_id"),
        )
