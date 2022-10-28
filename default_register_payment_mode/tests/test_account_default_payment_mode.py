# Copyright 2021 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields
from odoo.tests.common import Form, TransactionCase


class TestDefaultPaymentMode(TransactionCase):
    def _create_invoice(self, partner, payment_mode_id, default_move_type="in_invoice"):
        move_form = Form(
            self.env["account.move"].with_context(
                default_move_type=default_move_type, default_journal_id=self.journal.id
            )
        )
        move_form.partner_id = partner
        move_form.invoice_date = fields.Date.today()
        move_form.payment_mode_id = payment_mode_id
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product
            line_form.name = "product test cost 100"
            line_form.quantity = 1.0
            line_form.price_unit = 100.0
            line_form.account_id = self.account_expense
        return move_form.save()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # Company
        cls.company = cls.env.ref("base.main_company")
        cls.env.ref("base.EUR").active = True
        cls.journal_model = cls.env["account.journal"]
        cls.payment_mode_model = cls.env["account.payment.mode"]
        cls.journal = cls.journal_model.create(
            {
                "name": "Test journal",
                "type": "purchase",
                "code": "test-purchase-journal",
                "company_id": cls.company.id,
            }
        )
        cls.journal_c1 = cls.journal_model.create(
            {
                "name": "Fixed Journal - Company 1",
                "code": "fixed",
                "type": "bank",
                "company_id": cls.company.id,
            }
        )
        cls.journal_c2 = cls.journal_model.create(
            {
                "name": "Variable Journal - Company 1",
                "code": "variable",
                "type": "bank",
                "company_id": cls.company.id,
            }
        )
        cls.property_account_payable_id = cls.env["account.account"].create(
            {
                "name": "Test Payable Account",
                "code": "test_payable",
                "user_type_id": cls.env.ref("account.data_account_type_payable").id,
                "reconcile": True,
            }
        )
        cls.partner_1 = (
            cls.env["res.partner"]
            .with_company(cls.company.id)
            .create(
                {
                    "name": "Test Partner",
                    "supplier_rank": 1,
                    "property_account_payable_id": cls.property_account_payable_id.id,
                }
            )
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Test", "standard_price": 500.0}
        )
        cls.account_expense = cls.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TEST1",
                "user_type_id": cls.env.ref("account.data_account_type_expenses").id,
            }
        )

        # refs
        cls.manual_out = cls.env.ref("account.account_payment_method_manual_out")
        cls.payment_mode_variable_c1 = cls.payment_mode_model.create(
            {
                "name": "Payment Mode Variable Bank 1",
                "bank_account_link": "variable",
                "payment_method_id": cls.manual_out.id,
                "company_id": cls.company.id,
                "variable_journal_ids": [
                    (6, 0, [cls.journal_c1.id, cls.journal_c2.id])
                ],
            }
        )
        payment_mode_form = Form(cls.payment_mode_model)
        payment_mode_form.name = "Payment Mode Fixed Bank 1"
        payment_mode_form.bank_account_link = "fixed"
        payment_mode_form.payment_method_id = cls.manual_out
        payment_mode_form.company_id = cls.company
        payment_mode_form.fixed_journal_id = cls.journal_c1
        cls.payment_mode_fixed_c1 = payment_mode_form.save()

    def test_register_payment_fixed(self):
        invoice = self._create_invoice(
            partner=self.partner_1, payment_mode_id=self.payment_mode_fixed_c1
        )
        self.assertNotEqual(
            invoice.payment_mode_id, False, "Payment mode should be set on invoice"
        )
        invoice.action_post()
        payment_action = invoice.action_register_payment()
        payment = (
            self.env[payment_action["res_model"]]
            .with_context(**payment_action["context"])
            .create({})
        )
        self.assertEqual(
            payment.journal_id, self.journal_c1, "Journal should be the fixed one"
        )
        payment_method_line_id = self.env["account.payment.method.line"].search(
            [
                ("journal_id", "=", invoice.payment_mode_id.fixed_journal_id.id),
                (
                    "payment_method_id",
                    "=",
                    invoice.payment_mode_id.payment_method_id.id,
                ),
                ("payment_type", "=", invoice.payment_mode_id.payment_type),
            ],
            limit=1,
        )
        self.assertEqual(
            payment.payment_method_line_id,
            payment_method_line_id,
            "Payment method line should be the same",
        )

    def test_register_payment_variable(self):
        invoice_variable = self._create_invoice(
            partner=self.partner_1, payment_mode_id=self.payment_mode_variable_c1
        )
        self.assertNotEqual(
            invoice_variable.payment_mode_id,
            False,
            "Payment mode should be set on invoice",
        )
        invoice_variable.action_post()
        payment_action_variable = invoice_variable.action_register_payment()
        payment = (
            self.env[payment_action_variable["res_model"]]
            .with_context(**payment_action_variable["context"])
            .create({})
        )
        self.assertEqual(
            payment.journal_id,
            self.journal_c1 or self.journal_c2,
            "Journal should one of the variable ones",
        )
        payment_method_line_ids = self.env["account.payment.method.line"].search(
            [
                (
                    "journal_id",
                    "in",
                    invoice_variable.payment_mode_id.variable_journal_ids.ids,
                ),
                (
                    "payment_method_id",
                    "=",
                    invoice_variable.payment_mode_id.payment_method_id.id,
                ),
                ("payment_type", "=", invoice_variable.payment_mode_id.payment_type),
            ]
        )
        self.assertIn(
            payment.payment_method_line_id,
            payment_method_line_ids,
            "Payment method line should be in the list",
        )
