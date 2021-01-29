# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestVendorEmail(TransactionCase):
    def setUp(self):
        super(TestVendorEmail, self).setUp()

        # Company
        self.company = self.env.ref("base.main_company")

        self.journal_c1 = self.env["account.journal"].create(
            {
                "name": "Journal 1",
                "code": "J1",
                "type": "bank",
                "company_id": self.company.id,
            }
        )

        self.manual_out = self.env.ref("account.account_payment_method_manual_out")

        self.email_template = self.env.ref(
            "account_payment_order_vendor_email.ach_payment_email_template"
        )

        self.partner_id = self.env.ref("base.res_partner_12")

        self.payment_mode_c1 = self.env["account.payment.mode"].create(
            {
                "name": "Direct Debit of suppliers from Bank 1",
                "bank_account_link": "variable",
                "payment_method_id": self.manual_out.id,
                "company_id": self.company.id,
                "fixed_journal_id": self.journal_c1.id,
                "variable_journal_ids": [(6, 0, [self.journal_c1.id])],
                "send_email_to_partner": True,
                "email_temp_id": self.email_template.id,
            }
        )

    def test_send_vendor_email(self):
        self.payment_order_id = self.env["account.payment.order"].create(
            {
                "payment_mode_id": self.payment_mode_c1.id,
                "journal_id": self.journal_c1.id,
                "payment_type": "outbound",
                "payment_line_ids": [
                    (
                        0,
                        0,
                        {
                            "amount_currency": 200.00,
                            "partner_id": self.partner_id.id,
                            "communication": "TEST",
                        },
                    )
                ],
            }
        )
        self.payment_order_id.draft2open()
        self.payment_order_id.open2generated()
        self.payment_order_id.generated2uploaded()
        self.payment_order_id.send_vendor_email()
