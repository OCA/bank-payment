# Copyright 2024 Binhex - Adasat Torres de León.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from unittest.mock import MagicMock, patch

import plaid

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestPlaidInterface(common.TransactionCase):
    post_install = True

    def test_get_host(self):
        """Test getting Plaid host."""
        interface_model = self.env["plaid.interface"]
        self.assertEqual(interface_model._get_host("sand"), plaid.Environment.Sandbox)
        self.assertEqual(
            interface_model._get_host("prod"), plaid.Environment.Production
        )
        self.assertFalse(interface_model._get_host("nonexistent"))

    @patch("plaid.api.plaid_api.PlaidApi")
    def test_client(self, PlaidApi):
        interface_model = self.env["plaid.interface"]
        PlaidApi.return_value = MagicMock()
        client = interface_model._client("client_id", "secret", "sand")
        self.assertTrue(client)

    @patch(
        "plaid.api.plaid_api.PlaidApi",
        side_effect=plaid.ApiException("INVALID_SECRET", "This secret is invalid"),
    )
    def test_client_error(self, PlaidApi):
        interface_model = self.env["plaid.interface"]
        self.assertRaises(
            ValidationError, interface_model._client, "client_id", "secret2", "sandbox"
        )

    @patch("plaid.api.plaid_api.PlaidApi.link_token_create")
    def test_link(self, link_token_create):
        interface_model = self.env["plaid.interface"]
        link_token_create.return_value = MagicMock(
            to_dict=lambda: {"link_token": "isalinktoken", "expiration": "isadate"}
        )
        client = interface_model._client("client_id", "secret", "sand")
        link = interface_model._link(
            client=client,
            language="en",
            country_code="US",
            company_name="company",
            products=["transactions"],
        )
        self.assertTrue(link)
        self.assertEqual(link, "isalinktoken")

    @patch(
        "plaid.api.plaid_api.PlaidApi.link_token_create",
        side_effect=plaid.ApiException(
            "INVALID_CLIENT_ID", "This client id is invalid"
        ),
    )
    def test_link_error(self, link_token_create):
        interface_model = self.env["plaid.interface"]
        client = interface_model._client("client_id", "secret", "sand")
        self.assertRaises(
            ValidationError,
            interface_model._link,
            client,
            "en",
            "US",
            "company",
            ["transactions"],
        )

    @patch("plaid.api.plaid_api.PlaidApi.item_public_token_exchange")
    def test_login(self, item_public_token_exchange):
        interface_model = self.env["plaid.interface"]
        item_public_token_exchange.return_value = MagicMock(
            to_dict=lambda: {"access_token": "isaccesstoken"}
        )
        client = interface_model._client("client_id", "secret", "sand")
        public_token = "isapulbictoken"
        access_token = interface_model._login(client, public_token)
        self.assertTrue(access_token)

    @patch(
        "plaid.api.plaid_api.PlaidApi.item_public_token_exchange",
        side_effect=plaid.ApiException("INVALID_PUBLIC_TOKEN", "This token is invalid"),
    )
    def test_login_error(self, item_public_token_exchange):
        interface_model = self.env["plaid.interface"]
        client = interface_model._client("client_id", "secret", "sand")
        public_token = "isapulbictoken"
        self.assertRaises(ValidationError, interface_model._login, client, public_token)

    @patch("plaid.api.plaid_api.PlaidApi.accounts_get")
    def test_get_account(self, accounts_get):
        interface_model = self.env["plaid.interface"]
        accounts_get.return_value = MagicMock(
            to_dict=lambda: {
                "accounts": [
                    {
                        "account_id": "1",
                        "balances": {"available": 100},
                        "name": "account",
                    }
                ]
            }
        )
        client = interface_model._client("client_id", "secret", "sand")
        access_token = "isaccesstoken"
        accounts = interface_model._get_accounts(client, access_token)
        self.assertTrue(accounts)
        self.assertEqual(
            accounts,
            [{"account_id": "1", "balances": {"available": 100}, "name": "account"}],
        )

    @patch(
        "plaid.api.plaid_api.PlaidApi.accounts_get",
        side_effect=plaid.ApiException("INVALID_ACCESS_TOKEN", "This token is invalid"),
    )
    def test_get_account_error(self, accounts_get):
        interface_model = self.env["plaid.interface"]
        client = interface_model._client("client", "secret", "sand")
        with self.assertRaises(ValidationError):
            interface_model._get_accounts(client, "isnotaccesstoken")

    @patch("plaid.api.plaid_api.PlaidApi.transfer_authorization_create")
    def test_transfer_auth(self, transfer_authorization_create):
        interface_model = self.env["plaid.interface"]
        transfer_authorization_create.return_value = MagicMock(
            to_dict=lambda: {
                "authorization": {
                    "id": "1",
                    "decision": "approved",
                    "decision_rationale": "isarationale",
                }
            }
        )
        client = interface_model._client("client_id", "secret", "sand")
        access_token = "isaccesstoken"
        account_id = "1287689GHJGJjghj7876"
        partner_id = self.env["res.partner"].create(
            {"name": "partner", "plaid_client_id": "1897789HKJH98hjhgjh786"}
        )
        amount = "100.00"
        auth = interface_model._transfer_auth(
            client, access_token, account_id, partner_id, amount
        )
        self.assertTrue(auth)
        self.assertEqual(
            auth,
            {
                "authorization_id": "1",
                "decision": "approved",
                "decision_rationale": "isarationale",
            },
        )

    @patch(
        "plaid.api.plaid_api.PlaidApi.transfer_authorization_create",
        side_effect=plaid.ApiException("INVALID_ACCESS_TOKEN", "This token is invalid"),
    )
    def test_transfer_auth_error(self, transfer_authorization_create):
        interface_model = self.env["plaid.interface"]
        client = interface_model._client("client_id", "secret", "sand")
        access_token = "isaccesstoken"
        account_id = "1287689GHJGJjghj7876"
        partner_id = self.env["res.partner"].create(
            {"name": "partner", "plaid_client_id": "1897789HKJH98hjhgjh786"}
        )
        amount = "100.00"
        with self.assertRaises(ValidationError):
            interface_model._transfer_auth(
                client, access_token, account_id, partner_id, amount
            )

    @patch("plaid.api.plaid_api.PlaidApi.transfer_create")
    def test_transfer(self, transfer_create):
        interface_model = self.env["plaid.interface"]
        transfer_create.return_value = MagicMock(
            to_dict=lambda: {"transfer": {"id": "1", "status": "pending"}}
        )
        client = interface_model._client("client_id", "secret", "sand")
        access_token = "isaccesstoken"
        account_id = "1287689GHJGJjghj7876"
        amount = "100.00"
        transfer_id = interface_model._transfer(
            client, access_token, account_id, "ahjk8979-38979-dhjhg", amount
        )
        self.assertTrue(transfer_id)
        self.assertEqual(transfer_id["id"], "1")

    @patch(
        "plaid.api.plaid_api.PlaidApi.transfer_create",
        side_effect=plaid.ApiException("INVALID_ACCESS_TOKEN", "This token is invalid"),
    )
    def test_transfer_error(self, transfer_create):
        interface_model = self.env["plaid.interface"]
        client = interface_model._client("client_id", "secret", "sandbox")
        with self.assertRaises(ValidationError):
            interface_model._transfer(
                client,
                "isaccesstoken",
                "account",
                "ahjk8979-38979-dhjhg",
                "100.00",
            )

    @patch("plaid.api.plaid_api.PlaidApi.transfer_event_sync")
    def test_sync_transfer_events(self, transfer_event_sync):
        interface_model = self.env["plaid.interface"]
        transfer_event_sync.return_value = MagicMock(
            to_dict=lambda: {"transfer_events": [{"id": "1", "type": "transfer"}]}
        )
        client = interface_model._client("client_id", "secret", "sandbox")
        events = interface_model._sync_transfer_events(client)
        self.assertTrue(events)
        self.assertEqual(events, [{"id": "1", "type": "transfer"}])

    @patch(
        "plaid.api.plaid_api.PlaidApi.transfer_event_sync",
        side_effect=plaid.ApiException("INVALID_ACCESS_TOKEN", "This token is invalid"),
    )
    def test_sync_transfer_events_error(self, transfer_event_sync):
        interface_model = self.env["plaid.interface"]
        client = interface_model._client("client", "secret", "sandbox")
        with self.assertRaises(ValidationError):
            interface_model._sync_transfer_events(client)

    @patch(
        "plaid.api.plaid_api.PlaidApi.sandbox_transfer_simulate",
        side_effect=plaid.ApiException("INVALID_ACCESS_TOKEN", "This token is invalid"),
    )
    def test_sandbox_transfer_simulate(self, sandbox_simulate_transfer):
        interface_model = self.env["plaid.interface"]
        client = interface_model._client("client_id", "secret", "sandbox")
        with self.assertRaises(ValidationError):
            interface_model._sandbox_simulate_transfer(client, "1", "posted", 100)

    @patch(
        "plaid.api.plaid_api.PlaidApi.sandbox_transfer_ledger_simulate_available",
        side_effect=plaid.ApiException("INVALID_ACCESS_TOKEN", "This token is invalid"),
    )
    def test_sandbox_transfer_ledger_simulate_available(
        self, sandbox_transfer_ledger_simulate_available
    ):
        interface_model = self.env["plaid.interface"]
        client = interface_model._client("client_id", "secret", "sandbox")
        with self.assertRaises(ValidationError):
            interface_model._sandbox_transfer_ledger_simulate_available(client)
