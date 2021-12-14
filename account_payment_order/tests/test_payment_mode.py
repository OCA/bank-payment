# © 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.tests.common import TransactionCase

from odoo.addons.account.models.account_payment_method import AccountPaymentMethod


class TestPaymentMode(TransactionCase):
    def setUp(self):
        super(TestPaymentMode, self).setUp()

        Method_get_payment_method_information = (
            AccountPaymentMethod._get_payment_method_information
        )

        def _get_payment_method_information(self):
            res = Method_get_payment_method_information(self)
            res["IN"] = {"mode": "multi", "domain": [("type", "=", "bank")]}
            res["IN2"] = {"mode": "multi", "domain": [("type", "=", "bank")]}
            res["electronic_out"] = {"mode": "multi", "domain": [("type", "=", "bank")]}
            return res

        # Company
        self.company = self.env.ref("base.main_company")

        self.journal_c1 = self.env["account.journal"].create(
            {
                "name": "Journal 1",
                "code": "J1",
                "type": "bank",
                "company_id": self.company.id,
            }
        )

        self.account = self.env["account.account"].search(
            [("reconcile", "=", True), ("company_id", "=", self.company.id)], limit=1
        )

        self.manual_out = self.env.ref("account.account_payment_method_manual_out")

        self.manual_in = self.env.ref("account.account_payment_method_manual_in")

        with patch.object(
            AccountPaymentMethod,
            "_get_payment_method_information",
            _get_payment_method_information,
        ):

            self.electronic_out = self.env["account.payment.method"].create(
                {
                    "name": "Electronic Out",
                    "code": "electronic_out",
                    "payment_type": "outbound",
                }
            )

        self.payment_mode_c1 = self.env["account.payment.mode"].create(
            {
                "name": "Direct Debit of suppliers from Bank 1",
                "bank_account_link": "variable",
                "payment_method_id": self.manual_out.id,
                "company_id": self.company.id,
                "fixed_journal_id": self.journal_c1.id,
                "variable_journal_ids": [(6, 0, [self.journal_c1.id])],
            }
        )

    def test_onchange_generate_move(self):
        self.payment_mode_c1.generate_move = True
        self.payment_mode_c1.generate_move_change()
        self.assertEqual(self.payment_mode_c1.move_option, "date")
        self.payment_mode_c1.generate_move = False
        self.payment_mode_c1.generate_move_change()
        self.assertFalse(self.payment_mode_c1.move_option)

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
