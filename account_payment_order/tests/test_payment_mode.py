# © 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.addons.account.models.account_payment_method import AccountPaymentMethod
from odoo.addons.base.tests.common import BaseCommon


class TestPaymentMode(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Method_get_payment_method_information = (
            AccountPaymentMethod._get_payment_method_information
        )

        def _get_payment_method_information(cls):
            res = Method_get_payment_method_information(cls)
            res["IN"] = {"mode": "multi", "domain": [("type", "=", "bank")]}
            res["IN2"] = {"mode": "multi", "domain": [("type", "=", "bank")]}
            res["electronic_out"] = {"mode": "multi", "domain": [("type", "=", "bank")]}
            return res

        # Company
        cls.company = cls.env.ref("base.main_company")

        cls.journal_c1 = cls.env["account.journal"].create(
            {
                "name": "Journal 1",
                "code": "J1",
                "type": "bank",
                "company_id": cls.company.id,
            }
        )

        cls.account = cls.env["account.account"].search(
            [("reconcile", "=", True), ("company_ids", "in", cls.company.ids)], limit=1
        )

        cls.manual_out = cls.env.ref("account.account_payment_method_manual_out")

        cls.manual_in = cls.env.ref("account.account_payment_method_manual_in")

        with patch.object(
            AccountPaymentMethod,
            "_get_payment_method_information",
            _get_payment_method_information,
        ):
            cls.electronic_out = cls.env["account.payment.method"].create(
                {
                    "name": "Electronic Out",
                    "code": "electronic_out",
                    "payment_type": "outbound",
                }
            )

        cls.payment_mode_c1 = cls.env["account.payment.mode"].create(
            {
                "name": "Direct Debit of suppliers from Bank 1",
                "bank_account_link": "variable",
                "payment_method_id": cls.manual_out.id,
                "company_id": cls.company.id,
                "fixed_journal_id": cls.journal_c1.id,
                "variable_journal_ids": [(6, 0, [cls.journal_c1.id])],
            }
        )

    def test_onchange_payment_type(self):
        self.payment_mode_c1.payment_method_id = self.manual_in
        self.payment_mode_c1.payment_method_id_change()
        self.assertTrue(
            all(
                [
                    journal.type in ["sale_refund", "sale"]
                    for journal in self.payment_mode_c1.default_journal_ids
                ]
            )
        )
        self.payment_mode_c1.payment_method_id = self.manual_out
        self.payment_mode_c1.payment_method_id_change()
        self.assertTrue(
            all(
                [
                    journal.type in ["purchase_refund", "purchase"]
                    for journal in self.payment_mode_c1.default_journal_ids
                ]
            )
        )
