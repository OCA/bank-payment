# Copyright 2025 Simone Rubino
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestPartnerBank(AccountTestInvoicingCommon):
    def test_default_user_create(self):
        """The default user in tests can create partner bank accounts."""
        # Arrange
        partner_form = Form(self.env["res.partner"])
        partner_form.name = "Test Partner"
        partner = partner_form.save()

        # Act
        partner_bank_form = Form(self.env["res.partner.bank"])
        partner_bank_form.acc_number = "Test Account Number"
        partner_bank_form.partner_id = partner
        partner_bank = partner_bank_form.save()

        # Assert
        self.assertTrue(partner_bank)
