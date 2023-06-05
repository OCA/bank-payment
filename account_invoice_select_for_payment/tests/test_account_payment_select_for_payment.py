# Copyright 2023 Qubiq - Victor Aljaro
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestAccountPayment(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.payment = self.env["account.payment"].create({"name": "Test Payment"})

    def test_action_register_payment(self):
        # Create test moves
        move1 = self.env["account.move"].create(
            {"name": "Move 1", "selected_for_payment": True}
        )
        move2 = self.env["account.move"].create(
            {"name": "Move 2", "selected_for_payment": False}
        )
        move3 = self.env["account.move"].create(
            {"name": "Move 3", "selected_for_payment": True}
        )

        # Set active_ids context
        self.payment.with_context(
            active_ids=[move1.id, move2.id, move3.id]
        ).action_register_payment()

        # Verify selected_for_payment is False for move1 and move3
        self.assertFalse(move1.selected_for_payment)
        self.assertFalse(move2.selected_for_payment)
        self.assertFalse(move3.selected_for_payment)

    def test_action_register_payment_no_active_ids(self):
        # Call action_register_payment without active_ids context
        self.payment.action_register_payment()

        # No changes should be made
        self.assertFalse(
            self.payment.env["account.move"].search(
                [("selected_for_payment", "=", True)]
            )
        )
