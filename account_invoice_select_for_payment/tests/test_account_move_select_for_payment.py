# Copyright 2023 Qubiq - Victor Aljaro
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestAccountMove(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.move = self.env["account.move"].create({"name": "Test Move"})

    def test_action_toggle_select_for_payment(self):
        # Ensure selected_for_payment is initially False
        self.assertFalse(self.move.selected_for_payment)

        # Toggle selected_for_payment to True
        self.move.action_toggle_select_for_payment()
        self.assertTrue(self.move.selected_for_payment)

        # Toggle selected_for_payment back to False
        self.move.action_toggle_select_for_payment()
        self.assertFalse(self.move.selected_for_payment)

    def test_action_toggle_select_for_payment_multiple_moves(self):
        # Create multiple moves
        move1 = self.env["account.move"].create({"name": "Move 1"})
        move2 = self.env["account.move"].create({"name": "Move 2"})

        # Ensure selected_for_payment is initially False for all moves
        self.assertFalse(move1.selected_for_payment)
        self.assertFalse(move2.selected_for_payment)

        # Toggle selected_for_payment for move1
        move1.action_toggle_select_for_payment()
        self.assertTrue(move1.selected_for_payment)
        self.assertFalse(move2.selected_for_payment)

        # Toggle selected_for_payment for move2
        move2.action_toggle_select_for_payment()
        self.assertTrue(move1.selected_for_payment)
        self.assertTrue(move2.selected_for_payment)

        # Toggle selected_for_payment back to False for move1
        move1.action_toggle_select_for_payment()
        self.assertFalse(move1.selected_for_payment)
        self.assertTrue(move2.selected_for_payment)

        # Toggle selected_for_payment back to False for move2
        move2.action_toggle_select_for_payment()
        self.assertFalse(move1.selected_for_payment)
        self.assertFalse(move2.selected_for_payment)
