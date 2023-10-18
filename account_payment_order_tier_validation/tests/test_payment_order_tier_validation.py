# Copyright 2022 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# Copyright 2023, XCG Consulting
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import ValidationError
from odoo.tests import common, tagged


@tagged("-at_install", "post_install")
class TestPaymentOrderTierValidation(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Get payment order model
        cls.payment_order_model = cls.env.ref(
            "account_payment_order.model_account_payment_order"
        )

        # Create users
        group_ids = (
            cls.env.ref("base.group_system")
            | cls.env.ref("account_payment_order.group_account_payment")
        ).ids
        cls.test_user_1 = cls.env["res.users"].create(
            {
                "name": "John",
                "login": "test1",
                "groups_id": [(6, 0, group_ids)],
                "email": "test@examlple.com",
            }
        )

        # Create tier definitions:
        cls.tier_def_obj = cls.env["tier.definition"]
        cls.tier_def_obj.create(
            {
                "model_id": cls.payment_order_model.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user_1.id,
                "definition_domain": "[('total_company_currency', '>', 50.0)]",
            }
        )

        # Create Partner
        cls.partner = cls.env["res.partner"].create({"name": "Partner for test"})

        cls.company = cls.env.ref("base.main_company")
        cls.journal_c1 = cls.env["account.journal"].create(
            {
                "name": "Journal 1",
                "code": "J1",
                "type": "bank",
                "company_id": cls.company.id,
            }
        )

        # Create Payment Mode
        cls.mode = cls.env["account.payment.mode"].create(
            {
                "name": "Test Credit Transfer to Suppliers",
                "company_id": cls.company.id,
                "bank_account_link": "variable",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
            }
        )

        # Get Bank Journal
        cls.bank_journal = cls.env["account.journal"].search(
            [("company_id", "=", cls.company.id), ("type", "=", "bank")], limit=1
        )

    def test_tier_validation_model_name(self):
        self.assertIn(
            "account.payment.order",
            self.tier_def_obj._get_tier_validation_model_names(),
        )

    def test_validation_payment_order(self):
        po = self.env["account.payment.order"].create(
            {
                "payment_mode_id": 1,
                "payment_type": "outbound",
                "journal_id": self.bank_journal.id,
                "date_prefered": "now",
                "payment_line_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": self.partner.id,
                            "amount_currency": 1000,
                            "communication": "normal",
                        },
                    )
                ],
            }
        )
        with self.assertRaises(ValidationError):
            po.draft2open()
        po.request_validation()
        po.invalidate_recordset()
        po.with_user(self.test_user_1).validate_tier()
        po.draft2open()
        self.assertEqual(po.state, "open")
