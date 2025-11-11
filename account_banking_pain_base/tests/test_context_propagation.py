# Copyright 2025
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestOpen2GeneratedBankContext(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Company = cls.env.company
        cls.Bank = cls.env["res.bank"].sudo()
        cls.ResPartnerBank = cls.env["res.partner.bank"].sudo()
        cls.Journal = cls.env["account.journal"].sudo()
        cls.PaymentMode = cls.env["account.payment.mode"].sudo()
        cls.PaymentOrder = cls.env["account.payment.order"].sudo()
        cls.bank = cls.Bank.create({"name": "The Bank"})
        cls.partner_bank = cls.ResPartnerBank.create(
            {
                "acc_number": "NL00TRIO0123456789",
                "partner_id": cls.Company.partner_id.id,
                "bank_id": cls.bank.id,
            }
        )
        cls.journal = cls.Journal.create(
            {
                "name": "Hybrid Test The Bank",
                "type": "bank",
                "code": "HBD",
                "bank_account_id": cls.partner_bank.id,
                "company_id": cls.Company.id,
            }
        )
        manual_out = cls.env.ref("account.account_payment_method_manual_out")
        cls.pay_mode = cls.PaymentMode.create(
            {
                "name": "Hybrid Mode",
                "company_id": cls.Company.id,
                "payment_method_id": manual_out.id,
                "payment_type": "outbound",
                "bank_account_link": "fixed",
                "fixed_journal_id": cls.journal.id,
            }
        )
        cls.po = cls.PaymentOrder.create(
            {
                "name": "PO-HYB",
                "payment_mode_id": cls.pay_mode.id,
                "payment_type": "outbound",
                "journal_id": cls.journal.id,
            }
        )

    def test_open2generated_injects_bank_context(self):
        """open2generated must call generate_payment_file with export_bank_id in context."""
        captured = {}

        def fake_generate_payment_file(self_local):
            """Fake the base generate_payment_file response"""
            # Everything is the same, except setting this context key
            captured["export_bank_id"] = self_local.env.context.get("export_bank_id")
            # original return signature
            return (False, False)

        Model = type(self.po)
        # store original method
        original_generate_payment_file = Model.generate_payment_file
        try:
            # perform file generation operations with the fake method
            Model.generate_payment_file = fake_generate_payment_file
            self.po.open2generated()
        finally:
            # restore original method
            Model.generate_payment_file = original_generate_payment_file
        # bank_id was present in the active context during file generation
        self.assertEqual(self.po.state, "generated")
        self.assertEqual(
            captured.get("export_bank_id"),
            self.bank.id,
        )
