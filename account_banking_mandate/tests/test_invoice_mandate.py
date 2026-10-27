# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from unittest.mock import patch

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from odoo.addons.account.models.account_payment_method import AccountPaymentMethod

from .common import AccountBankingMandateCommon


@tagged("post_install", "-at_install")
class TestInvoiceMandate(AccountBankingMandateCommon):
    def test_01_post_invoice_propagates_mandate_to_remittance(self):
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
        payment_line = payment_order.payment_line_ids
        self.assertEqual(payment_line.mandate_id, self.mandate)
        self.assertEqual(payment_line.partner_bank_id, self.partner_bank)
        payment_order.payment_mode_id_change()
        payment_order.draft2open()
        payment_order.open2generated()
        payment_order.generated2uploaded()
        self.assertEqual(self.mandate.payment_line_ids_count, 1)

    def test_02_post_invoice_rejects_mandate_from_another_company(self):
        partner_2 = self._create_res_partner("Jane with ACME Bank")
        partner_2.customer_payment_mode_id = self.mode_inbound_acme
        bank_account = self._create_partner_bank(
            self.env, partner_2, "0023032234211", self.company_2
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

    def test_03_post_invoice_and_refund_keep_mandate(self):
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

    def test_04_onchange_partner_selects_compatible_mandate(self):
        partner_2 = self._create_res_partner("Jane with ACME Bank")
        partner_2.customer_payment_mode_id = self.mode_inbound_acme
        bank_account = self._create_partner_bank(
            self.env, partner_2, "0023032234211", self.company
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

    def test_05_manual_mandate_selection_is_preserved(self):
        self.alternative_mandate.validate()
        self.assertEqual(self.invoice.mandate_id, self.mandate)
        self.invoice.mandate_id = self.alternative_mandate
        self.assertEqual(self.invoice.mandate_id, self.alternative_mandate)

    def test_06_onchange_non_mandate_payment_mode_clears_mandate(self):
        Method_get_payment_method_information = (
            AccountPaymentMethod._get_payment_method_information
        )

        def _get_payment_method_information(self):
            res = Method_get_payment_method_information(self)
            res["test"] = {"mode": "multi", "type": ("bank",)}
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

    def test_07_invoice_rejects_mandate_from_another_company(self):
        partner_2 = self._create_res_partner("Jane with ACME Bank")
        partner_2.customer_payment_mode_id = self.mode_inbound_acme
        bank_account = self._create_partner_bank(
            self.env, partner_2, "0023032234211", self.company_2
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

    def test_08_open_payment_order_rejects_missing_mandate(self):
        self.invoice.action_post()
        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=self.invoice.ids
        ).create({}).run()

        payment_order = self.env["account.payment.order"].search([])
        payment_order.payment_line_ids.mandate_id = False
        with self.assertRaises(UserError):
            payment_order.draft2open()

    def test_09_payment_line_rejects_bank_different_from_mandate(self):
        self.invoice.action_post()
        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=self.invoice.ids
        ).create({}).run()

        payment_line = self.env["account.payment.order"].search([]).payment_line_ids
        with self.assertRaises(ValidationError):
            payment_line.partner_bank_id = self.alternative_bank_account

    def test_10_supplier_payment_does_not_require_mandate(self):
        supplier_mode = self.env["account.payment.mode"].create(
            {
                "name": "Outbound supplier payment",
                "company_id": self.company.id,
                "bank_account_link": "variable",
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
                "payment_order_ok": True,
            }
        )
        supplier_mode.variable_journal_ids = self.env["account.journal"].search(
            [("type", "=", "bank"), ("company_id", "=", self.company.id)],
            limit=1,
        )
        supplier = self._create_res_partner("Supplier without mandate")
        supplier.supplier_payment_mode_id = supplier_mode
        bill = self.env["account.move"].create(
            {
                "partner_id": supplier.id,
                "move_type": "in_invoice",
                "company_id": self.company.id,
                "invoice_date": fields.Date.today(),
                "journal_id": self.env["account.journal"]
                .search(
                    [("type", "=", "purchase"), ("company_id", "=", self.company.id)],
                    limit=1,
                )
                .id,
                "payment_mode_id": supplier_mode.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 1.0,
                            "account_id": self.invoice_line_account.id,
                            "price_unit": 200.00,
                        },
                    )
                ],
            }
        )
        bill.action_post()
        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=bill.ids
        ).create({}).run()

        payment_order = self.env["account.payment.order"].search([])
        self.assertEqual(payment_order.payment_type, "outbound")
        self.assertFalse(payment_order.payment_line_ids.mandate_id)
        payment_order.payment_mode_id_change()
        payment_order.payment_line_ids.communication = bill.name
        payment_order.draft2open()

    def _create_res_partner(self, name):
        return self.env["res.partner"].create({"name": name})

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
                ("company_ids", "in", [cls.company.id]),
            ],
            limit=1,
        )
        cls.invoice_line_account = cls.env["account.account"].search(
            [
                ("account_type", "=", "expense"),
                ("company_ids", "in", [cls.company.id]),
            ],
            limit=1,
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "type": "service",
            }
        )
        invoice_vals = [
            (
                0,
                0,
                {
                    "product_id": cls.product.id,
                    "quantity": 1.0,
                    "account_id": cls.invoice_line_account.id,
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
