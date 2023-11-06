# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestPurchaseRequest(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.tier_definition = self.env["tier.definition"]

    def test_get_tier_validation_model_names(self):
        self.assertIn(
            "account.payment.order",
            self.tier_definition._get_tier_validation_model_names(),
        )
