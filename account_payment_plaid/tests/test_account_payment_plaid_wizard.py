# Copyright 2024 Binhex - Adasat Torres de León.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from unittest.mock import MagicMock, patch

from odoo.exceptions import ValidationError
from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestAccountPaymentPlaidWizard(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountPaymentPlaidWizard, cls).setUpClass()

        cls.plaid_account = cls.env["plaid.account"].create(
            {
                "name": "Test Plaid Account",
                "account": "TestAccount",
            }
        )

        cls.company_id = cls.env.user.company_id
        cls.company_id.plaid_account_id = cls.plaid_account.id
        cls.company_id.write(
            {
                "plaid_client_id": "TestClientId",
                "plaid_secret": "TestSecret",
                "plaid_access_token": "PlaidAccessToken",
            }
        )

        cls.partner_id = cls.env["res.partner"].create(
            {"name": "Test Partner", "plaid_client_id": "OriginatorClientID"}
        )
        cls.account_move_id = cls.env["account.move"].create(
            {
                "name": "Test Account Move",
                "partner_id": cls.partner_id.id,
                "journal_id": cls.env.ref("account.data_account_type_receivable").id,
                "amount_total": 100.0,
                "company_id": cls.company_id.id,
            }
        )

        cls.account_payment_plaid_wizard = cls.env[
            "account.payment.plaid.wizard"
        ].create(
            {
                "account_move_id": cls.account_move_id.id,
                "amount": 100.0,
                "currency_id": cls.env.ref("base.USD").id,
                "description": "Test Description",
                "partner_id": cls.partner_id.id,
                "company_id": cls.company_id.id,
            }
        )

    def test_verify_plaid_auth(self):
        decision = {
            "decision": "approved",
            "decision_rationale": {
                "code": "TestError",
                "description": "Test Description Error",
            },
            "authorization_id": "TestSuccess",
        }

        auth = self.account_payment_plaid_wizard._verify_plaid_auth(decision)
        self.assertEqual(auth, "TestSuccess")

    def test_verify_plaid_auth_error(self):
        decision = {
            "decision": "rejected",
            "decision_rationale": {
                "code": "TestError",
                "description": "Test Description Error",
            },
            "authorization_id": "TestSuccess",
        }

        with self.assertRaises(ValidationError):
            self.account_payment_plaid_wizard._verify_plaid_auth(decision)

    @patch("plaid.api.plaid_api.PlaidApi.transfer_create")
    @patch("plaid.api.plaid_api.PlaidApi.transfer_authorization_create")
    def test_action_confirm(self, transfer_authorization_create, transfer_create):
        transfer_authorization_create.return_value = MagicMock(
            to_dict=lambda: {
                "authorization": {
                    "id": "TestAuthSuccess",
                    "decision": "approved",
                    "decision_rationale": {
                        "code": "TestError",
                        "description": "Test Description Error",
                    },
                }
            }
        )
        transfer_create.return_value = MagicMock(
            to_dict=lambda: {
                "transfer": {
                    "id": "TestTransferSuccess",
                    "status": "pending",
                    "amount": "100.00",
                    "description": "Test Description",
                }
            }
        )
        self.account_payment_plaid_wizard.action_confirm()
        self.assertTrue(
            self.env["plaid.transfer"].search(
                [
                    ("name", "=", "TestTransferSuccess"),
                ]
            )
        )

    def test_create_transfer(self):
        transfer = {
            "id": "TestTransferSuccess",
            "status": "pending",
        }
        res = self.account_payment_plaid_wizard._create_transfer(transfer)
        self.assertTrue(res)
