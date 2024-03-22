# Copyright 2023 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import odoo.tests
from odoo import fields

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@odoo.tests.tagged("post_install", "-at_install")
class TestPaymentOrderTranserJournal(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        today = fields.Date.today()
        cls.in_invoice = cls.init_invoice(
            "in_invoice", invoice_date=today, products=cls.product_a
        )
        cls.bank_journal = cls.company_data["default_journal_bank"]
        cls.misc_journal = cls.company_data["default_journal_misc"]
        cls.payment_mode = cls.env["account.payment.mode"].create(
            {
                "name": "Test Credit Transfer to Suppliers",
                "company_id": cls.env.company.id,
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
                "fixed_journal_id": cls.bank_journal.id,
                "bank_account_link": "fixed",
            }
        )

    def test_payment_order_transfer_journal(self):
        self.in_invoice._post()
        self.payment_mode.transfer_journal_id = self.misc_journal
        ap_aml = self.in_invoice.line_ids.filtered(
            lambda r: r.account_type == "liability_payable"
        )
        payline_vals = {
            "move_line_id": ap_aml.id,
            "partner_id": self.in_invoice.partner_id.id,
            "communication": "F0123",
            "amount_currency": -ap_aml.amount_currency,
        }
        order_vals = {
            "payment_type": "outbound",
            "payment_mode_id": self.payment_mode.id,
            "payment_line_ids": [(0, 0, payline_vals)],
        }
        order = self.env["account.payment.order"].create(order_vals)
        order.draft2open()
        self.assertEqual(order.mapped("move_ids.journal_id"), self.misc_journal)
