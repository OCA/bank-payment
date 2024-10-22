from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestAccountMove(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountMove, cls).setUpClass()
        cls.account_move = cls.env["account.move"].create(
            {
                "name": "Test Account Move",
                "partner_id": cls.env["res.partner"]
                .create({"name": "Test Partner"})
                .id,
                "amount_total": 100.0,
                "currency_id": cls.env.ref("base.USD").id,
                "company_id": cls.env.user.company_id.id,
            }
        )

    def test_action_payment_with_plaid_wizard(self):
        action = self.account_move.action_payment_with_plaid_wizard()
        self.assertTrue(action)
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "account.payment.plaid.wizard")
        self.assertEqual(
            action["context"],
            {
                "default_partner_id": self.account_move.partner_id.id,
                "default_account_move_id": self.account_move.id,
                "default_amount": self.account_move.amount_total,
                "default_currency_id": self.account_move.currency_id.id,
                "default_description": self.account_move.name,
                "default_company_id": self.account_move.company_id.id,
            },
        )
        self.assertEqual(action["target"], "new")
