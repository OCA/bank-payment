from unittest.mock import MagicMock, patch

from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestPlaidTransfer(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPlaidTransfer, cls).setUpClass()

        cls.company_id = cls.env.user.company_id
        cls.account_move_id = cls.env["account.move"].create(
            {
                "name": "Test Account Move",
                "company_id": cls.company_id.id,
                "amount_total": 100.0,
            }
        )
        cls.plaid_transfer = cls.env["plaid.transfer"].create(
            {
                "name": "TestPlaidTransfer",
                "description": "Test Description",
                "amount": 100.0,
                "state": "pending",
                "currency_id": cls.env.ref("base.USD").id,
                "company_id": cls.company_id.id,
                "account_move_id": cls.account_move_id.id,
            }
        )

    def test_action_sandbox_simulation(self):
        action = self.plaid_transfer.action_sandbox_simulation()

        self.assertTrue(action)
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(
            action["res_model"], "plaid.transfer.sandbox.simulation.wizard"
        )
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["target"], "new")
        self.assertEqual(
            action["context"],
            {
                "default_transfer_id": self.plaid_transfer.id,
                "default_company_id": self.plaid_transfer.company_id.id,
            },
        )

    @patch("plaid.api.plaid_api.PlaidApi.transfer_event_sync")
    def test_cron_sync_transfer_events(self, transfer_event_sync):

        transfer_event_sync.return_value = MagicMock(
            to_dict=lambda: {
                "transfer_events": [
                    {"transfer_id": "TestPlaidTransfer", "event_type": "posted"}
                ]
            }
        )
        self.env["plaid.transfer"].cron_sync_transfer_events()
        self.assertEqual(self.plaid_transfer.state, "posted")
