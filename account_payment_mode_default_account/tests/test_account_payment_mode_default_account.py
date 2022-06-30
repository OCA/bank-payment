# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import Form, SavepointCase


class TestAccountPaymentModeDefaultAccount(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chart_template = cls.env.company.chart_template_id
        chart_template.try_loading(company=cls.env.company)
        receivable_code = chart_template["property_account_receivable_id"].code
        cls.receivable_account = cls.env["account.account"].search(
            [
                ("company_id", "=", cls.env.company.id),
                ("user_type_id.type", "=", "receivable"),
                ("code", "=like", receivable_code + "%"),
            ],
            limit=1,
        )
        cls.payable_account = cls.env["account.account"].search(
            [
                ("company_id", "=", cls.env.company.id),
                ("user_type_id.type", "=", "payable"),
            ],
            limit=1,
        )
        cls.receivable_account2 = cls.receivable_account.copy(
            {"code": cls.receivable_account.code + "2"}
        )
        cls.payable_account2 = cls.payable_account.copy(
            {"code": cls.payable_account.code + "2"}
        )
        cls.partner_1 = cls.env.ref("base.res_partner_1")

        cls.payment_mode = cls.env.ref("account_payment_mode.payment_mode_inbound_dd1")
        cls.payment_mode.write(
            {
                "default_receivable_account_id": cls.receivable_account2.id,
                "default_payable_account_id": cls.payable_account2.id,
            }
        )
        cls.payment_mode_without_default = cls.env.ref(
            "account_payment_mode.payment_mode_inbound_ct1"
        )

    @classmethod
    def _create_invoice(cls, move_type="out_invoice", payment_mode=None):
        move_form = Form(
            cls.env["account.move"].with_context(default_move_type=move_type)
        )
        move_form.partner_id = cls.partner_1
        if payment_mode is not None:
            move_form.payment_mode_id = payment_mode
        with move_form.invoice_line_ids.new() as line_form:
            line_form.name = "test"
            line_form.quantity = 1.0
            line_form.price_unit = 100
        invoice = move_form.save()
        return invoice

    def test_create_customer_invoice_payment_mode_default(self):
        invoice = self._create_invoice(payment_mode=self.payment_mode)
        payment_term_line = invoice._get_payment_term_lines()
        self.assertEqual(payment_term_line.account_id, self.receivable_account2)

    def test_create_supplier_invoice_payment_mode_default(self):
        invoice = self._create_invoice(
            move_type="in_invoice", payment_mode=self.payment_mode
        )
        payment_term_line = invoice._get_payment_term_lines()
        self.assertEqual(payment_term_line.account_id, self.payable_account2)

    def test_change_customer_invoice_payment_mode_default(self):
        invoice = self._create_invoice()
        payment_term_line = invoice._get_payment_term_lines()
        self.assertEqual(payment_term_line.account_id, self.receivable_account)
        with Form(invoice) as move_form:
            move_form.payment_mode_id = self.payment_mode
        self.assertEqual(payment_term_line.account_id, self.receivable_account2)

    def test_change_supplier_invoice_payment_mode_default(self):
        invoice = self._create_invoice(move_type="in_invoice")
        payment_term_line = invoice._get_payment_term_lines()
        self.assertEqual(payment_term_line.account_id, self.payable_account)
        with Form(invoice) as move_form:
            move_form.payment_mode_id = self.payment_mode
        self.assertEqual(payment_term_line.account_id, self.payable_account2)

    def test_create_customer_invoice_payment_mode_without_default(self):
        invoice = self._create_invoice(payment_mode=self.payment_mode_without_default)
        payment_term_line = invoice._get_payment_term_lines()
        self.assertEqual(payment_term_line.account_id, self.receivable_account)

    def test_create_supplier_invoice_payment_mode_without_default(self):
        invoice = self._create_invoice(
            move_type="in_invoice", payment_mode=self.payment_mode_without_default
        )
        payment_term_line = invoice._get_payment_term_lines()
        self.assertEqual(payment_term_line.account_id, self.payable_account)

    def test_change_customer_invoice_payment_mode_without_default(self):
        invoice = self._create_invoice()
        payment_term_line = invoice._get_payment_term_lines()
        self.assertEqual(payment_term_line.account_id, self.receivable_account)
        with Form(invoice) as move_form:
            move_form.payment_mode_id = self.payment_mode_without_default
        self.assertEqual(payment_term_line.account_id, self.receivable_account)

    def test_change_supplier_invoice_payment_mode_without_default(self):
        invoice = self._create_invoice(move_type="in_invoice")
        payment_term_line = invoice._get_payment_term_lines()
        self.assertEqual(payment_term_line.account_id, self.payable_account)
        with Form(invoice) as move_form:
            move_form.payment_mode_id = self.payment_mode_without_default
        self.assertEqual(payment_term_line.account_id, self.payable_account)

    def test_partner_compute_inverse(self):
        self.assertEqual(
            self.partner_1.property_account_receivable_id, self.receivable_account
        )
        self.assertEqual(
            self.partner_1.property_account_payable_id, self.payable_account
        )
        self.assertEqual(
            self.partner_1.with_context(
                _partner_property_account_payment_mode=self.payment_mode.id
            ).property_account_receivable_id,
            self.receivable_account2,
        )
        self.assertEqual(
            self.partner_1.with_context(
                _partner_property_account_payment_mode=self.payment_mode.id
            ).property_account_payable_id,
            self.payable_account2,
        )
        self.partner_1.write(
            {
                "property_account_receivable_id": self.receivable_account2.id,
                "property_account_payable_id": self.payable_account2.id,
            }
        )
        self.assertEqual(
            self.partner_1.property_account_receivable_id, self.receivable_account2
        )
        self.assertEqual(
            self.partner_1.property_account_payable_id, self.payable_account2
        )
