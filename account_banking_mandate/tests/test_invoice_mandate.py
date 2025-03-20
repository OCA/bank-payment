# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from unittest.mock import patch

from odoo import Command, fields
from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.account.models.account_payment_method import AccountPaymentMethod
from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestInvoiceMandate(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.test_company = cls.setup_other_company(
            name="TEST Banking Mandate company",
        )
        cls.company = cls.company_data["company"]
        cls.company_2 = cls.test_company["company"]
        cls.env.user.write(
            {
                "groups_id": [
                    Command.link(
                        cls.env.ref("account_payment_order.group_account_payment").id
                    )
                ],
                "company_ids": [
                    Command.link(cls.company_2.id),
                    Command.link(cls.company.id),
                ],
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Peter with ACME Bank"})
        cls.acme_bank = cls.env["res.bank"].create(
            {
                "name": "ACME Bank",
                "bic": "GEBABEBB03B",
            }
        )

        bank_account = cls.env["res.partner.bank"].create(
            {
                "acc_number": "FR92 1234 5678 9012 4469 5309 A98",
                "partner_id": cls.partner.id,
                "bank_id": cls.acme_bank.id,
                "company_id": cls.company.id,
            }
        )

        cls.mandate = cls.env["account.banking.mandate"].create(
            {
                "partner_bank_id": bank_account.id,
                "signature_date": "2015-01-01",
                "company_id": cls.company.id,
            }
        )

        cls.mandate.validate()
        cls.bank_journal = cls.env["account.journal"].search(
            [
                ("type", "=", "bank"),
                ("company_id", "=", cls.company.id),
            ],
            limit=1,
        )
        cls.mode_inbound_acme = cls.env["account.payment.method.line"].create(
            {
                "name": "Inbound Credit ACME Bank",
                "company_id": cls.company.id,
                "bank_account_link": "variable",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
                "journal_id": cls.bank_journal.id,
                "payment_order_ok": True,
                "selectable": True,
            }
        )
        cls.mode_inbound_acme.payment_method_id.mandate_required = True

        cls.partner.with_company(
            cls.company.id
        ).property_inbound_payment_method_line_id = cls.mode_inbound_acme

        cls.invoice_account = cls.company_data["default_account_receivable"]
        cls.invoice = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "move_type": "out_invoice",
                "company_id": cls.company.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.env.ref("product.product_product_4").id,
                            "quantity": 1.0,
                            "price_unit": 200.00,
                        }
                    )
                ],
            }
        )

    def test_post_invoice_01(self):
        self.assertEqual(self.invoice.mandate_id, self.mandate)

        self.invoice.action_post()

        payable_move_lines = self.invoice.line_ids.filtered(
            lambda s: s.account_id == self.invoice_account
        )
        if payable_move_lines:
            self.assertEqual(payable_move_lines[0].move_id.mandate_id, self.mandate)

        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=self.invoice.ids
        ).create({}).run()

        payment_order = self.env["account.payment.order"].search([])
        self.assertEqual(len(payment_order.ids), 1)
        payment_order.draft2open()
        payment_order.open2generated()
        payment_order.generated2uploaded()
        self.assertEqual(self.mandate.payment_line_ids_count, 1)

    def test_post_invoice_02(self):
        partner_2 = self.env["res.partner"].create({"name": "Jane with ACME Bank"})
        partner_2.with_company(
            self.company.id
        ).property_inbound_payment_method_line_id = self.mode_inbound_acme
        bank_account = self.env["res.partner.bank"].create(
            {
                "acc_number": "FR63 1234 5678 9012 4744 7548 A98",
                "partner_id": partner_2.id,
                "bank_id": self.acme_bank.id,
                "company_id": self.company_2.id,
            }
        )

        mandate_2 = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": bank_account.id,
                "signature_date": "2015-01-01",
                "company_id": self.company_2.id,
            }
        )
        mandate_2.validate()

        self.assertEqual(self.invoice.mandate_id, self.mandate)
        self.invoice.action_post()

        payable_move_lines = self.invoice.line_ids.filtered(
            lambda s: s.account_id == self.invoice_account
        )
        if payable_move_lines:
            with self.assertRaises(UserError):
                payable_move_lines[0].move_id.mandate_id = mandate_2

    def test_post_invoice_and_refund_02(self):
        self.invoice.action_post()
        self.assertEqual(self.invoice.mandate_id, self.mandate)
        move_reversal = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=self.invoice.ids)
            .create(
                {
                    "date": fields.Date.today(),
                    "reason": "no reason",
                    "journal_id": self.invoice.journal_id.id,
                }
            )
        )
        reversal = move_reversal.reverse_moves()
        ref = self.env["account.move"].browse(reversal["res_id"])
        self.assertEqual(self.invoice.mandate_id, ref.mandate_id)

    def test_onchange_partner(self):
        partner_2 = self.env["res.partner"].create({"name": "Jane with ACME Bank"})
        partner_2.with_company(
            self.company.id
        ).property_inbound_payment_method_line_id = self.mode_inbound_acme
        bank_account = self.env["res.partner.bank"].create(
            {
                "acc_number": "FR48 1234 5678 9012 5781 5617 A98",
                "partner_id": partner_2.id,
                "bank_id": self.acme_bank.id,
                "company_id": self.company.id,
            }
        )

        mandate_2 = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": bank_account.id,
                "signature_date": "2015-01-01",
                "company_id": self.company.id,
            }
        )
        mandate_2.validate()

        invoice = self.env["account.move"].new(
            {
                "partner_id": self.partner.id,
                "move_type": "out_invoice",
                "company_id": self.company.id,
            }
        )

        invoice.partner_id = partner_2
        self.assertEqual(invoice.mandate_id, mandate_2)

    def test_onchange_payment_mode(self):
        Method_get_payment_method_information = (
            AccountPaymentMethod._get_payment_method_information
        )

        def _get_payment_method_information(self):
            res = Method_get_payment_method_information(self)
            res["test"] = {"mode": "multi", "domain": [("type", "=", "bank")]}
            return res

        invoice = self.env["account.move"].new(
            {
                "partner_id": self.partner.id,
                "move_type": "out_invoice",
                "company_id": self.company.id,
            }
        )

        with patch.object(
            AccountPaymentMethod,
            "_get_payment_method_information",
            _get_payment_method_information,
        ):
            pay_method_test = self.env["account.payment.method"].create(
                {
                    "name": "Test",
                    "code": "test",
                    "payment_type": "inbound",
                    "mandate_required": False,
                }
            )
        mode_inbound_acme_2 = self.env["account.payment.method.line"].create(
            {
                "name": "Inbound Credit ACME Bank 2",
                "company_id": self.company.id,
                "bank_account_link": "variable",
                "payment_method_id": pay_method_test.id,
                "journal_id": self.bank_journal.id,
            }
        )

        invoice.preferred_payment_method_line_id = mode_inbound_acme_2
        self.assertEqual(invoice.mandate_id, self.env["account.banking.mandate"])
