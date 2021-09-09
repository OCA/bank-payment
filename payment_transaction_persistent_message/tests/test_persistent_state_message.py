# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import odoo.tests.common as common


class TestPersistentStateMessage(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.acquirer = cls.env.ref("payment.payment_acquirer_odoo_by_adyen")
        vals = {
            "acquirer_id": cls.acquirer.id,
            "type": "validation",
            "amount": 10.0,
            "currency_id": cls.env.user.company_id.currency_id.id,
        }
        cls.transaction = cls.env["payment.transaction"].create(vals)

    def test_state_message(self):
        # Write a value in state_message field
        # set transaction_done
        # state_message is void but persistent_state_message is set
        self.transaction.write(
            {
                "state_message": "A first message",
            }
        )
        self.assertEqual(
            "A first message",
            self.transaction.state_message,
        )
        self.assertEqual(
            "A first message",
            self.transaction.persistent_state_message,
        )
        self.transaction._set_transaction_pending()
        self.assertFalse(
            self.transaction.state_message,
        )
        self.assertEqual(
            "A first message",
            self.transaction.persistent_state_message,
        )
        self.transaction.write(
            {
                "state_message": "A second message",
            }
        )
        self.assertEqual(
            "A first message\nA second message",
            self.transaction.persistent_state_message,
        )
        self.transaction._set_transaction_done()
        self.assertFalse(
            self.transaction.state_message,
        )
        self.assertEqual(
            "A first message\nA second message",
            self.transaction.persistent_state_message,
        )
