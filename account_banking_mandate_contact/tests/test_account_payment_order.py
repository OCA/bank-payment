# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl

from unittest.mock import patch

from odoo import fields
from odoo.tests.common import Form, TransactionCase

from odoo.addons.account.models.account_payment_method import AccountPaymentMethod


class TestAccountPaymentOrder(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Test Partner"})
        self.product = self.env["product.product"].create({"name": "Test product"})
        self.partner_bank_core = self._create_res_partner_bank("N-CORE")
        self.mandate_core = self._create_mandate(self.partner_bank_core, "CORE")
        self.partner_bank_b2b = self._create_res_partner_bank("N-B2B")
        self.mandate_b2b = self._create_mandate(self.partner_bank_b2b, "B2B")
        payment_method_vals = {
            "name": "SEPA",
            "code": "sepa_direct_debit",
            "payment_type": "inbound",
            "bank_account_required": True,
        }
        self.method_sepa = self._create_multi_bank_payment_method(payment_method_vals)
        self.journal_bank = self.env["account.journal"].create(
            {"name": "BANK", "type": "bank", "code": "bank"}
        )
        payment_form = Form(self.env["account.payment.mode"])
        payment_form.name = "SEPA (CORE)"
        payment_form.payment_method_id = self.method_sepa
        payment_form.bank_account_link = "fixed"
        payment_form.fixed_journal_id = self.journal_bank
        payment_form.payment_order_ok = True
        self.payment_core = payment_form.save()
        self.payment_b2b = self.payment_core.copy({"name": "SEPA B2B"})
        self.partner.customer_payment_mode_id = self.payment_core.id
        self.env["account.journal"].create(
            {"name": "SALE", "type": "sale", "code": "sale"}
        )
        self.invoice = self._create_invoice()
        payment_order_form = Form(
            self.env["account.payment.order"].with_context(
                default_payment_type="inbound"
            )
        )
        payment_order_form.payment_mode_id = self.payment_core
        self.payment_order = payment_order_form.save()

    def _create_multi_bank_payment_method(self, payment_method_vals):
        method_get_payment_method_information = (
            AccountPaymentMethod._get_payment_method_information
        )

        def _get_payment_method_information(self):
            res = method_get_payment_method_information(self)
            res[payment_method_vals["code"]] = {
                "mode": "multi",
                "domain": [("type", "=", "bank")],
            }
            return res

        with patch.object(
            AccountPaymentMethod,
            "_get_payment_method_information",
            _get_payment_method_information,
        ):
            return self.env["account.payment.method"].create(payment_method_vals)

    def _create_res_partner_bank(self, acc_number):
        res_partner_bank_form = Form(self.env["res.partner.bank"])
        res_partner_bank_form.partner_id = self.partner
        res_partner_bank_form.acc_number = acc_number
        return res_partner_bank_form.save()

    def _create_mandate(self, partner_bank, scheme):
        mandate_form = Form(self.env["account.banking.mandate"])
        mandate_form.partner_bank_id = partner_bank
        mandate_form.signature_date = fields.Date.from_string("2021-01-01")
        mandate = mandate_form.save()
        mandate.validate()
        return mandate

    def _create_invoice(self):
        invoice_form = Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        )
        invoice_form.partner_id = self.partner
        invoice_form.invoice_date = fields.Date.from_string("2021-01-01")
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product
            line_form.quantity = 1
            line_form.price_unit = 30
            line_form.tax_ids.clear()
        invoice = invoice_form.save()
        invoice.action_post()
        return invoice

    def test_invoice_payment_mode(self):
        self.assertEqual(self.invoice.state, "posted")
        self.assertEqual(self.invoice.payment_mode_id, self.payment_core)
        self.assertEqual(
            self.invoice.invoice_date_due, fields.Date.from_string("2021-01-01")
        )

    def test_account_payment_order_core(self):
        line_create_form = Form(
            self.env["account.payment.line.create"].with_context(
                active_model="account.payment.order", active_id=self.payment_order.id
            )
        )
        line_create_form.date_type = "due"
        line_create_form.due_date = fields.Date.from_string("2021-01-01")
        line_create = line_create_form.save()
        line_create.populate()
        line_create.create_payment_lines()
        self.assertAlmostEqual(len(self.payment_order.payment_line_ids), 1)
        payment_line = self.payment_order.payment_line_ids.filtered(
            lambda x: x.partner_id == self.partner
        )
        self.assertEqual(payment_line.partner_bank_id, self.partner_bank_core)

    def test_account_payment_order_core_extra(self):
        self.partner.contact_mandate_id = self.mandate_b2b
        line_create_form = Form(
            self.env["account.payment.line.create"].with_context(
                active_model="account.payment.order", active_id=self.payment_order.id
            )
        )
        line_create_form.date_type = "due"
        line_create_form.due_date = fields.Date.from_string("2021-01-01")
        line_create = line_create_form.save()
        line_create.populate()
        line_create.create_payment_lines()
        self.assertAlmostEqual(len(self.payment_order.payment_line_ids), 1)
        payment_line = self.payment_order.payment_line_ids.filtered(
            lambda x: x.partner_id == self.partner
        )
        self.assertEqual(payment_line.partner_bank_id, self.partner_bank_b2b)
