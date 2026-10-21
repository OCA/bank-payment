# © 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon


class TestBank(BaseCommon):
    _test_user_groups = (
        "base.group_user",
        "base.group_partner_manager",
        "account.group_account_manager",
        "account_payment_order.group_account_payment",
    )

    def test_bank(self):
        bank = self.env["res.partner.bank"].search([], limit=1)
        if not bank:
            # This should only happen if we don't have demo data
            partner = self.env["res.partner"].create({"name": "Fiducial Banque"})
            bank = self.env["res.partner.bank"].create(
                {
                    "partner_id": partner.id,
                    "account_number": "FR7630006000011234567890189",
                    "bank_name": "Fiducial Banque",
                    "bank_bic": "FIDCFR21XXX",
                    "street": "38 rue Sergent Michel Berthet",
                    "zip": "69009",
                    "city": "Lyon",
                    "country_id": self.env.ref("base.fr").id,
                }
            )
        with self.assertRaises(ValidationError):
            bank.bank_bic = "TEST"
