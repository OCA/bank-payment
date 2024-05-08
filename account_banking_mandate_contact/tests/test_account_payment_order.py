# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl

from odoo import fields
from odoo.tests.common import Form, TransactionCase


class TestAccountPaymentOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create({"name": "Test product"})
        cls.partner_bank_core = cls._create_res_partner_bank("N-CORE")
        cls.mandate_core = cls._create_mandate(cls.partner_bank_core, "CORE")
        cls.partner_bank_b2b = cls._create_res_partner_bank("N-B2B")
        cls.mandate_b2b = cls._create_mandate(cls.partner_bank_b2b, "B2B")
        payment_method_vals = {
            "name": "SEPA",
            "code": "sepa_direct_debit",
            "payment_type": "inbound",
            "bank_account_required": True,
        }
        cls.method_sepa = cls.env["account.payment.method"].create(payment_method_vals)
        cls.journal_bank = cls.env["account.journal"].create(
            {
                "name": "BANK",
                "type": "bank",
                "code": "bank",
            }
        )
        payment_form = Form(cls.env["account.payment.mode"])
        payment_form.name = "SEPA (CORE)"
        payment_form.payment_method_id = cls.method_sepa
        payment_form.bank_account_link = "fixed"
        payment_form.fixed_journal_id = cls.journal_bank
        payment_form.payment_order_ok = True
        cls.payment_core = payment_form.save()
        cls.payment_b2b = cls.payment_core.copy({"name": "SEPA B2B"})
        cls.partner.customer_payment_mode_id = cls.payment_core.id
        cls.env["account.journal"].create(
            {"name": "SALE", "type": "sale", "code": "sale"}
        )
        cls.invoice = cls._create_invoice()
        payment_order_form = Form(
            cls.env["account.payment.order"].with_context(
                default_payment_type="inbound"
            )
        )
        payment_order_form.payment_mode_id = cls.payment_core
        cls.payment_order = payment_order_form.save()

    @classmethod
    def _create_res_partner_bank(cls, acc_number):
        res_partner_bank_form = Form(cls.env["res.partner.bank"])
        res_partner_bank_form.partner_id = cls.partner
        res_partner_bank_form.acc_number = acc_number
        return res_partner_bank_form.save()

    @classmethod
    def _create_mandate(cls, partner_bank, scheme):
        mandate_form = Form(cls.env["account.banking.mandate"])
        mandate_form.partner_bank_id = partner_bank
        mandate_form.signature_date = fields.Date.from_string("2021-01-01")
        mandate = mandate_form.save()
        mandate.validate()
        return mandate

    @classmethod
    def _create_invoice(cls):
        invoice_form = Form(
            cls.env["account.move"].with_context(default_move_type="out_invoice")
        )
        invoice_form.partner_id = cls.partner
        invoice_form.invoice_date = fields.Date.from_string("2021-01-01")
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = cls.product
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
