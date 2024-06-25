# Copyright 2024 Binhex - Adasat Torres de León.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from unittest.mock import MagicMock, patch

from odoo.tests import common


class TestResConfigSettings(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestResConfigSettings, cls).setUpClass()
        cls.company = cls.env["res.company"].create(
            {
                "name": "Test Company",
                "plaid_client_id": "test_client_id",
                "plaid_secret": "test_secret",
                "plaid_host": "sand",
            }
        )
        cls.config_settings = cls.env["res.config.settings"].create(
            {"company_id": cls.company.id}
        )

    @patch("plaid.api.plaid_api.PlaidApi.link_token_create")
    def test_action_sync_with_plaid(self, link_token_create):
        link_token_create.return_value = MagicMock(
            to_dict=lambda: {"link_token": "isalinktoken", "expiration": "isadate"}
        )
        action = self.config_settings.action_sync_with_plaid()
        self.assertTrue(action)
        self.assertEqual(action["type"], "ir.actions.client")
        self.assertEqual(action["tag"], "plaid_login")
        self.assertEqual(action["params"]["token"], "isalinktoken")
