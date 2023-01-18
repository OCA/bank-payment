# Copyright 2017 ForgeFlow S.L.
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Date
from odoo.tests.common import Form, TransactionCase


class TestAccountPaymentPartner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.res_users_model = cls.env["res.users"]
        cls.move_model = cls.env["account.move"]
        cls.journal_model = cls.env["account.journal"]
        cls.payment_mode_model = cls.env["account.payment.mode"]
        cls.partner_bank_model = cls.env["res.partner.bank"]

        # Refs
        cls.company = cls.env.ref("base.main_company")

        cls.company_2 = cls.env["res.company"].create({"name": "Company 2"})
        charts = cls.env["account.chart.template"].search([])
        if charts:
            cls.chart = charts[0]
        else:
            raise ValidationError(_("No Chart of Account Template has been defined !"))
        old_company = cls.env.user.company_id
        cls.env.user.company_id = cls.company_2.id
        cls.env.ref("base.user_admin").company_ids = [(4, cls.company_2.id)]
        cls.chart.try_loading()
        cls.env.user.company_id = old_company.id

        # refs
        cls.manual_out = cls.env.ref("account.account_payment_method_manual_out")
        cls.manual_out.bank_account_required = True
        cls.manual_in = cls.env.ref("account.account_payment_method_manual_in")

        cls.journal_sale = cls.env["account.journal"].create(
            {
                "name": "Test Sales Journal",
                "code": "tSAL",
                "type": "sale",
                "company_id": cls.company.id,
            }
        )

        cls.journal_purchase = cls.env["account.journal"].create(
            {
                "name": "Test Purchases Journal",
                "code": "tPUR",
                "type": "purchase",
                "company_id": cls.company.id,
            }
        )

        cls.journal_c1 = cls.journal_model.create(
            {
                "name": "J1",
                "code": "J1",
                "type": "bank",
                "company_id": cls.company.id,
                "bank_acc_number": "123456",
            }
        )

        cls.journal_c2 = cls.journal_model.create(
            {
                "name": "J2",
                "code": "J2",
                "type": "bank",
                "company_id": cls.company_2.id,
                "bank_acc_number": "552344",
            }
        )

        cls.supplier_payment_mode = cls.payment_mode_model.create(
            {
                "name": "Suppliers Bank 1",
                "bank_account_link": "variable",
                "payment_method_id": cls.manual_out.id,
                "show_bank_account_from_journal": True,
                "company_id": cls.company.id,
                "fixed_journal_id": cls.journal_c1.id,
                "variable_journal_ids": [(6, 0, [cls.journal_c1.id])],
            }
        )

        cls.supplier_payment_mode_c2 = cls.payment_mode_model.create(
            {
                "name": "Suppliers Bank 2",
                "bank_account_link": "variable",
                "payment_method_id": cls.manual_out.id,
                "company_id": cls.company_2.id,
                "fixed_journal_id": cls.journal_c2.id,
                "variable_journal_ids": [(6, 0, [cls.journal_c2.id])],
            }
        )

        cls.customer_payment_mode = cls.payment_mode_model.create(
            {
                "name": "Customers to Bank 1",
                "bank_account_link": "variable",
                "payment_method_id": cls.manual_in.id,
                "company_id": cls.company.id,
                "fixed_journal_id": cls.journal_c1.id,
                "refund_payment_mode_id": cls.supplier_payment_mode.id,
                "variable_journal_ids": [(6, 0, [cls.journal_c1.id])],
            }
        )
        cls.supplier_payment_mode.write(
            {"refund_payment_mode_id": cls.customer_payment_mode.id}
        )

        cls.customer = (
            cls.env["res.partner"]
            .with_company(cls.company.id)
            .create(
                {
                    "name": "Test customer",
                    "customer_payment_mode_id": cls.customer_payment_mode,
                }
            )
        )

        cls.supplier = (
            cls.env["res.partner"]
            .with_company(cls.company.id)
            .create(
                {
                    "name": "Test supplier",
                    "supplier_payment_mode_id": cls.supplier_payment_mode,
                }
            )
        )
        cls.supplier_bank = cls.env["res.partner.bank"].create(
            {
                "acc_number": "5345345",
                "partner_id": cls.supplier.id,
            }
        )
        cls.supplier.with_company(
            cls.company_2.id
        ).supplier_payment_mode_id = cls.supplier_payment_mode_c2

        cls.invoice_account = cls.env["account.account"].search(
            [
                ("account_type", "=", "liability_payable"),
                ("company_id", "=", cls.company.id),
            ],
            limit=1,
        )
        cls.invoice_line_account = cls.env["account.account"].search(
            [
                ("account_type", "=", "expense"),
                ("company_id", "=", cls.company.id),
            ],
            limit=1,
        )
        cls.journal_bank = cls.env["res.partner.bank"].create(
            {
                "acc_number": "GB95LOYD87430237296288",
                "partner_id": cls.env.user.company_id.partner_id.id,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "BANK TEST",
                "code": "TEST",
                "type": "bank",
                "bank_account_id": cls.journal_bank.id,
            }
        )
        cls.supplier_invoice = cls.move_model.create(
            {
                "partner_id": cls.supplier.id,
                "invoice_date": fields.Date.today(),
                "move_type": "in_invoice",
                "journal_id": cls.journal_purchase.id,
            }
        )

    def _create_invoice(self, default_move_type, partner):
        move_form = Form(
            self.env["account.move"].with_context(default_move_type=default_move_type)
        )
        move_form.partner_id = partner
        move_form.invoice_date = Date.today()
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.env.ref("product.product_product_4")
            line_form.name = "product that cost 100"
            line_form.quantity = 1.0
            line_form.price_unit = 100.0
        return move_form.save()

    def test_create_partner(self):
        customer = (
            self.env["res.partner"]
            .with_company(self.company.id)
            .create(
                {
                    "name": "Test customer",
                    "customer_payment_mode_id": self.customer_payment_mode,
                }
            )
        )

        self.assertEqual(
            customer.with_company(self.company.id).customer_payment_mode_id,
            self.customer_payment_mode,
        )
        self.assertEqual(
            customer.with_company(self.company_2.id).customer_payment_mode_id,
            self.payment_mode_model,
        )

    def test_partner_id_changes_compute_partner_bank(self):
        # Test _compute_partner_bank is executed when partner_id changes
        move_form = Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        )
        self.assertFalse(move_form.partner_bank_id)
        move_form.partner_id = self.customer
        self.assertEqual(move_form.payment_mode_id, self.customer_payment_mode)
        self.assertFalse(move_form.partner_bank_id)

    def test_out_invoice_onchange(self):
        # Test the onchange methods in invoice
        invoice = self.move_model.new(
            {
                "partner_id": self.customer.id,
                "move_type": "out_invoice",
                "company_id": self.company.id,
            }
        )
        self.assertEqual(invoice.payment_mode_id, self.customer_payment_mode)

        invoice.company_id = self.company_2
        self.assertEqual(invoice.payment_mode_id, self.payment_mode_model)

        invoice.payment_mode_id = False
        self.assertFalse(invoice.partner_bank_id)

    def test_invoice_create_in_invoice(self):
        invoice = self._create_invoice(
            default_move_type="in_invoice", partner=self.supplier
        )
        invoice.action_post()
        aml = invoice.line_ids.filtered(
            lambda l: l.account_id.account_type == "liability_payable"
        )
        self.assertEqual(invoice.payment_mode_id, aml[0].payment_mode_id)
        # Test payment mode change on aml
        mode = self.supplier_payment_mode.copy()
        aml.payment_mode_id = mode
        self.assertEqual(invoice.payment_mode_id, mode)
        # Test payment mode editability on account move
        self.assertFalse(invoice.has_reconciled_items)
        invoice.payment_mode_id = self.supplier_payment_mode
        self.assertEqual(aml.payment_mode_id, self.supplier_payment_mode)

    def test_invoice_create_out_invoice(self):
        invoice = self._create_invoice(
            default_move_type="out_invoice", partner=self.customer
        )
        invoice.action_post()
        aml = invoice.line_ids.filtered(
            lambda l: l.account_id.account_type == "asset_receivable"
        )
        self.assertEqual(invoice.payment_mode_id, aml[0].payment_mode_id)

    def test_invoice_create_out_refund(self):
        self.manual_out.bank_account_required = False
        invoice = self._create_invoice(
            default_move_type="out_refund", partner=self.customer
        )
        invoice.action_post()
        self.assertEqual(
            invoice.payment_mode_id,
            self.customer.customer_payment_mode_id.refund_payment_mode_id,
        )

    def test_invoice_create_in_refund(self):
        self.manual_in.bank_account_required = False
        invoice = self._create_invoice(
            default_move_type="in_refund", partner=self.supplier
        )
        invoice.action_post()
        self.assertEqual(
            invoice.payment_mode_id,
            self.supplier.supplier_payment_mode_id.refund_payment_mode_id,
        )

    def test_invoice_constrains(self):
        with self.assertRaises(UserError):
            self.move_model.create(
                {
                    "partner_id": self.supplier.id,
                    "move_type": "in_invoice",
                    "invoice_date": fields.Date.today(),
                    "company_id": self.company.id,
                    "payment_mode_id": self.supplier_payment_mode_c2.id,
                }
            )

    def test_payment_mode_constrains_01(self):
        self.move_model.create(
            {
                "partner_id": self.supplier.id,
                "move_type": "in_invoice",
                "invoice_date": fields.Date.today(),
                "company_id": self.company.id,
            }
        )
        with self.assertRaises(UserError):
            self.supplier_payment_mode.company_id = self.company_2

    def test_payment_mode_constrains_02(self):
        self.move_model.create(
            {
                "date": fields.Date.today(),
                "journal_id": self.journal_sale.id,
                "name": "/",
                "ref": "reference",
                "state": "draft",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": self.invoice_account.id,
                            "credit": 1000,
                            "debit": 0,
                            "name": "Test",
                            "ref": "reference",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": self.invoice_line_account.id,
                            "credit": 0,
                            "debit": 1000,
                            "name": "Test",
                            "ref": "reference",
                        },
                    ),
                ],
            }
        )
        with self.assertRaises(UserError):
            self.supplier_payment_mode.company_id = self.company_2

    def test_invoice_in_refund(self):
        invoice = self._create_invoice(
            default_move_type="in_invoice", partner=self.supplier
        )
        invoice.partner_bank_id = False
        invoice.action_post()
        # Lets create a refund invoice for invoice_1.
        # I refund the invoice Using Refund Button.
        refund_invoice_wizard = (
            self.env["account.move.reversal"]
            .with_context(
                **{
                    "active_ids": [invoice.id],
                    "active_id": invoice.id,
                    "active_model": "account.move",
                }
            )
            .create(
                {
                    "refund_method": "refund",
                    "reason": "reason test create",
                    "journal_id": invoice.journal_id.id,
                }
            )
        )
        refund_invoice = self.move_model.browse(
            refund_invoice_wizard.reverse_moves()["res_id"]
        )
        self.assertEqual(
            refund_invoice.payment_mode_id,
            invoice.payment_mode_id.refund_payment_mode_id,
        )
        self.assertEqual(refund_invoice.partner_bank_id, invoice.partner_bank_id)

    def test_invoice_out_refund(self):
        invoice = self._create_invoice(
            default_move_type="out_invoice", partner=self.customer
        )
        invoice.partner_bank_id = False
        invoice.action_post()
        # Lets create a refund invoice for invoice_1.
        # I refund the invoice Using Refund Button.
        refund_invoice_wizard = (
            self.env["account.move.reversal"]
            .with_context(
                **{
                    "active_ids": [invoice.id],
                    "active_id": invoice.id,
                    "active_model": "account.move",
                }
            )
            .create(
                {
                    "refund_method": "refund",
                    "reason": "reason test create",
                    "journal_id": invoice.journal_id.id,
                }
            )
        )
        refund_invoice = self.move_model.browse(
            refund_invoice_wizard.reverse_moves()["res_id"]
        )

        self.assertEqual(
            refund_invoice.payment_mode_id,
            invoice.payment_mode_id.refund_payment_mode_id,
        )
        self.assertEqual(refund_invoice.partner_bank_id, invoice.partner_bank_id)

    def test_partner(self):
        self.customer.write({"customer_payment_mode_id": self.customer_payment_mode.id})
        self.assertEqual(
            self.customer.customer_payment_mode_id, self.customer_payment_mode
        )

    def test_partner_onchange(self):
        customer_invoice = self.move_model.create(
            {"partner_id": self.customer.id, "move_type": "out_invoice"}
        )
        self.assertEqual(customer_invoice.payment_mode_id, self.customer_payment_mode)

        self.assertEqual(self.supplier_invoice.partner_bank_id, self.supplier_bank)
        vals = {"partner_id": self.customer.id, "move_type": "out_refund"}
        invoice = self.move_model.new(vals)
        self.assertEqual(invoice.payment_mode_id, self.supplier_payment_mode)
        vals = {"partner_id": self.supplier.id, "move_type": "in_refund"}
        invoice = self.move_model.new(vals)
        self.assertEqual(invoice.payment_mode_id, self.customer_payment_mode)
        vals = {"partner_id": False, "move_type": "out_invoice"}
        invoice = self.move_model.new(vals)
        self.assertFalse(invoice.payment_mode_id)
        vals = {"partner_id": False, "move_type": "out_refund"}
        invoice = self.move_model.new(vals)
        self.assertFalse(invoice.partner_bank_id)
        vals = {"partner_id": False, "move_type": "in_invoice"}
        invoice = self.move_model.new(vals)
        self.assertFalse(invoice.partner_bank_id)
        vals = {"partner_id": False, "move_type": "in_refund"}
        invoice = self.move_model.new(vals)
        self.assertFalse(invoice.partner_bank_id)

    def test_onchange_payment_mode_id(self):
        mode = self.supplier_payment_mode
        mode.payment_method_id.bank_account_required = True
        self.supplier_invoice.partner_bank_id = self.supplier_bank.id
        self.supplier_invoice.payment_mode_id = mode.id
        self.assertEqual(self.supplier_invoice.partner_bank_id, self.supplier_bank)
        mode.payment_method_id.bank_account_required = False
        self.assertEqual(self.supplier_invoice.partner_bank_id, self.supplier_bank)
        self.supplier_invoice.payment_mode_id = False
        self.assertFalse(self.supplier_invoice.partner_bank_id)

    def test_print_report(self):
        self.supplier_invoice.partner_bank_id = self.supplier_bank.id
        report = self.env.ref("account.account_invoices")
        res = str(report._render_qweb_html(report.id, self.supplier_invoice.ids)[0])
        # self.assertIn(self.supplier_bank.acc_number, res)
        payment_mode = self.supplier_payment_mode
        payment_mode.show_bank_account_from_journal = True
        self.supplier_invoice.payment_mode_id = payment_mode.id
        self.supplier_invoice.partner_bank_id = False
        res = str(report._render_qweb_html(report.id, self.supplier_invoice.ids)[0])
        self.assertIn(self.journal_c1.bank_acc_number, res)
        payment_mode.bank_account_link = "variable"
        payment_mode.variable_journal_ids = [(6, 0, self.journal.ids)]
        res = str(report._render_qweb_html(report.id, self.supplier_invoice.ids)[0])
        self.assertIn(self.journal_bank.acc_number, res)

    def test_filter_type_domain(self):
        in_invoice = self.move_model.create(
            {
                "partner_id": self.supplier.id,
                "move_type": "in_invoice",
                "invoice_date": fields.Date.today(),
                "journal_id": self.journal_purchase.id,
            }
        )
        self.assertEqual(in_invoice.payment_mode_filter_type_domain, "outbound")
        self.assertEqual(
            in_invoice.partner_bank_filter_type_domain, in_invoice.commercial_partner_id
        )
        out_refund = self.move_model.create(
            {
                "partner_id": self.customer.id,
                "move_type": "out_refund",
                "journal_id": self.journal_sale.id,
            }
        )
        self.assertEqual(out_refund.payment_mode_filter_type_domain, "outbound")
        self.assertEqual(
            out_refund.partner_bank_filter_type_domain, out_refund.commercial_partner_id
        )
        in_refund = self.move_model.create(
            {
                "partner_id": self.supplier.id,
                "move_type": "in_refund",
                "journal_id": self.journal_purchase.id,
            }
        )
        self.assertEqual(in_refund.payment_mode_filter_type_domain, "inbound")
        self.assertEqual(
            in_refund.partner_bank_filter_type_domain, in_refund.bank_partner_id
        )
        out_invoice = self.move_model.create(
            {
                "partner_id": self.customer.id,
                "move_type": "out_invoice",
                "journal_id": self.journal_sale.id,
            }
        )
        self.assertEqual(out_invoice.payment_mode_filter_type_domain, "inbound")
        self.assertEqual(
            out_invoice.partner_bank_filter_type_domain, out_invoice.bank_partner_id
        )

    def test_account_move_payment_mode_id_default(self):
        payment_mode = self.env.ref("account_payment_mode.payment_mode_inbound_dd1")
        field = self.env["ir.model.fields"].search(
            [
                ("model_id.model", "=", self.move_model._name),
                ("name", "=", "payment_mode_id"),
            ]
        )
        move_form = Form(
            self.move_model.with_context(
                default_name="Invoice test", default_move_type="out_invoice"
            )
        )
        self.assertFalse(move_form.payment_mode_id)
        self.env["ir.default"].create(
            {"field_id": field.id, "json_value": payment_mode.id}
        )
        move_form = Form(
            self.move_model.with_context(
                default_name="Invoice test", default_move_type="out_invoice"
            )
        )
        self.assertEqual(move_form.payment_mode_id, payment_mode)
