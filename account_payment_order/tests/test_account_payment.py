# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestAccountPayment(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.company = cls.company_data["company"]
        cls.env.user.company_ids += cls.company

        # MODELS
        cls.account_payment_model = cls.env["account.payment"]
        cls.account_journal_model = cls.env["account.journal"]
        cls.payment_method_model = cls.env["account.payment.method"]

        # INSTANCES
        # Payment methods
        cls.inbound_payment_method_01 = cls.payment_method_model.create(
            {
                "name": "inbound",
                "code": "IN",
                "payment_type": "inbound",
            }
        )
        cls.inbound_payment_method_02 = cls.inbound_payment_method_01.copy(
            {
                "name": "inbound 2",
                "code": "IN2",
            }
        )
        cls.outbound_payment_method_01 = cls.payment_method_model.create(
            {
                "name": "outbound",
                "code": "OUT",
                "payment_type": "outbound",
            }
        )
        # Journals
        cls.bank_journal = cls.company_data["default_journal_bank"]
        cls.bank_journal.inbound_payment_method_ids = [
            (
                6,
                0,
                [cls.inbound_payment_method_01.id, cls.inbound_payment_method_02.id],
            )
        ]
        cls.bank_journal.outbound_payment_method_ids = [
            (6, 0, [cls.outbound_payment_method_01.id])
        ]

    def test_account_payment_01(self):
        self.assertFalse(self.inbound_payment_method_01.payment_order_only)
        self.assertFalse(self.inbound_payment_method_02.payment_order_only)
        self.assertFalse(self.bank_journal.inbound_payment_order_only)
        self.inbound_payment_method_01.payment_order_only = True
        self.assertTrue(self.inbound_payment_method_01.payment_order_only)
        self.assertFalse(self.inbound_payment_method_02.payment_order_only)
        self.assertFalse(self.bank_journal.inbound_payment_order_only)
        self.inbound_payment_method_02.payment_order_only = True
        self.assertTrue(self.inbound_payment_method_01.payment_order_only)
        self.assertTrue(self.inbound_payment_method_02.payment_order_only)
        self.assertTrue(self.bank_journal.inbound_payment_order_only)

    def test_account_payment_02(self):
        self.assertFalse(self.outbound_payment_method_01.payment_order_only)
        self.assertFalse(self.bank_journal.outbound_payment_order_only)
        self.outbound_payment_method_01.payment_order_only = True
        self.assertTrue(self.outbound_payment_method_01.payment_order_only)
        self.assertTrue(self.bank_journal.outbound_payment_order_only)

    def test_account_payment_03(self):
        self.assertFalse(self.inbound_payment_method_01.payment_order_only)
        self.assertFalse(self.inbound_payment_method_02.payment_order_only)
        self.assertFalse(self.bank_journal.inbound_payment_order_only)
        new_account_payment = self.account_payment_model.with_context(
            default_company_id=self.company.id
        ).new(
            {
                "journal_id": self.bank_journal.id,
                "payment_type": "inbound",
                "amount": 1,
                "company_id": self.company.id,
            }
        )
        # check journals
        journals = new_account_payment._get_default_journal()
        self.assertIn(self.bank_journal, journals)
        # check payment methods
        payment_methods = new_account_payment.available_payment_method_ids.ids
        self.assertIn(self.inbound_payment_method_01.id, payment_methods)
        self.assertIn(self.inbound_payment_method_02.id, payment_methods)
        # Set one payment method of the bank journal 'payment order only'
        self.inbound_payment_method_01.payment_order_only = True
        # check journals
        journals = new_account_payment._get_default_journal()
        self.assertIn(self.bank_journal, journals)
        # check payment methods
        new_account_payment._compute_payment_method_fields()
        payment_methods = new_account_payment.available_payment_method_ids.ids
        self.assertNotIn(self.inbound_payment_method_01.id, payment_methods)
        self.assertIn(self.inbound_payment_method_02.id, payment_methods)
        # Set all payment methods of the bank journal 'payment order only'
        self.inbound_payment_method_02.payment_order_only = True
        self.assertTrue(self.inbound_payment_method_01.payment_order_only)
        self.assertTrue(self.inbound_payment_method_02.payment_order_only)
        self.assertTrue(self.bank_journal.inbound_payment_order_only)
        # check journals
        journals = new_account_payment._get_default_journal()
        self.assertNotIn(self.bank_journal, journals)
        # check payment methods
        new_account_payment._compute_payment_method_fields()
        payment_methods = new_account_payment.available_payment_method_ids.ids
        self.assertNotIn(self.inbound_payment_method_01.id, payment_methods)
        self.assertNotIn(self.inbound_payment_method_02.id, payment_methods)
