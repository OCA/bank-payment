# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from unittest.mock import patch

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

from odoo.addons.account.models.account_payment_method import AccountPaymentMethod
from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestInvoiceMandate(TransactionCase):
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
        payment_order.payment_mode_id_change()
        payment_order.draft2open()
        payment_order.open2generated()
        payment_order.generated2uploaded()
        self.assertEqual(self.mandate.payment_line_ids_count, 1)

    def test_post_invoice_02(self):
        partner_2 = self._create_res_partner("Jane with ACME Bank")
        partner_2.customer_payment_mode_id = self.mode_inbound_acme
        bank_account = self.env["res.partner.bank"].create(
            {
                "acc_number": "0023032234211",
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
                    "refund_method": "refund",
                    "journal_id": self.invoice.journal_id.id,
                }
            )
        )
        reversal = move_reversal.reverse_moves()
        ref = self.env["account.move"].browse(reversal["res_id"])
        self.assertEqual(self.invoice.mandate_id, ref.mandate_id)

    def test_onchange_partner(self):
        partner_2 = self._create_res_partner("Jane with ACME Bank")
        partner_2.customer_payment_mode_id = self.mode_inbound_acme
        bank_account = self.env["res.partner.bank"].create(
            {
                "acc_number": "0023032234211",
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
        mode_inbound_acme_2 = self.env["account.payment.mode"].create(
            {
                "name": "Inbound Credit ACME Bank 2",
                "company_id": self.company.id,
                "bank_account_link": "variable",
                "payment_method_id": pay_method_test.id,
            }
        )

        invoice.payment_mode_id = mode_inbound_acme_2
        self.assertEqual(invoice.mandate_id, self.env["account.banking.mandate"])

    def test_invoice_constrains(self):
        partner_2 = self._create_res_partner("Jane with ACME Bank")
        partner_2.customer_payment_mode_id = self.mode_inbound_acme
        bank_account = self.env["res.partner.bank"].create(
            {
                "acc_number": "0023032234211",
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

        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "move_type": "out_invoice",
                "company_id": self.company.id,
            }
        )

        with self.assertRaises(UserError):
            invoice.mandate_id = mandate_2

    @classmethod
    def _create_res_partner(cls, name):
        return cls.env["res.partner"].create({"name": name})

    @classmethod
    def _create_res_bank(cls, name, bic, city, country):
        return cls.env["res.bank"].create(
            {"name": name, "bic": bic, "city": city, "country": country.id}
        )

    @classmethod
    def setUpClass(cls):
        res = super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.company = cls.env.ref("base.main_company")
        cls.partner = cls._create_res_partner("Peter with ACME Bank")
        cls.acme_bank = cls._create_res_bank(
            "ACME Bank", "GEBABEBB03B", "Charleroi", cls.env.ref("base.be")
        )
        bank_account = cls.env["res.partner.bank"].create(
            {
                "acc_number": "0023032234211123",
                "partner_id": cls.partner.id,
                "bank_id": cls.acme_bank.id,
                "company_id": cls.company.id,
            }
        )
        cls.company_2 = cls.env["res.company"].create({"name": "Company 2"})
        cls.mandate = cls.env["account.banking.mandate"].create(
            {
                "partner_bank_id": bank_account.id,
                "signature_date": "2015-01-01",
                "company_id": cls.company.id,
            }
        )
        cls.mandate.validate()
        cls.mode_inbound_acme = cls.env["account.payment.mode"].create(
            {
                "name": "Inbound Credit ACME Bank",
                "company_id": cls.company.id,
                "bank_account_link": "variable",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
            }
        )
        bank_journal = cls.env["account.journal"].search(
            [
                ("type", "=", "bank"),
                ("company_id", "=", cls.company.id),
            ],
            limit=1,
        )
        cls.mode_inbound_acme.variable_journal_ids = bank_journal
        cls.mode_inbound_acme.payment_method_id.mandate_required = True
        cls.mode_inbound_acme.payment_order_ok = True
        cls.partner.customer_payment_mode_id = cls.mode_inbound_acme
        cls.invoice_account = cls.env["account.account"].search(
            [
                ("account_type", "=", "asset_receivable"),
                ("company_id", "=", cls.company.id),
            ],
            limit=1,
        )
        invoice_line_account = (
            cls.env["account.account"]
            .search(
                [
                    ("account_type", "=", "expense"),
                    ("company_id", "=", cls.company.id),
                ],
                limit=1,
            )
            .id
        )
        invoice_vals = [
            (
                0,
                0,
                {
                    "product_id": cls.env.ref("product.product_product_4").id,
                    "quantity": 1.0,
                    "account_id": invoice_line_account,
                    "price_unit": 200.00,
                },
            )
        ]
        cls.invoice = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "move_type": "out_invoice",
                "company_id": cls.company.id,
                "journal_id": cls.env["account.journal"]
                .search(
                    [("type", "=", "sale"), ("company_id", "=", cls.company.id)],
                    limit=1,
                )
                .id,
                "invoice_line_ids": invoice_vals,
            }
        )
        return res
