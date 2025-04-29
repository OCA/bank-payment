# Copyright 2025 Studio73 - Eugenio Micó <eugenio@studio73.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestSaleOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.company = cls.env.user.company_id
        cls.bank = cls.env["res.bank"].create(
            {
                "name": "Test Bank",
                "bic": "TESTBICX",
            }
        )
        cls.partner_bank = cls.env["res.partner.bank"].create(
            {
                "acc_number": "ES9121000418450200051332",
                "partner_id": cls.partner.id,
                "bank_id": cls.bank.id,
                "company_id": cls.company.id,
            }
        )
        cls.payment_method = cls.env["account.payment.method"].create(
            {
                "name": "SEPA Direct Debit",
                "mandate_required": True,
                "payment_type": "inbound",
                "code": "sepa_direct_debit",
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Test Bank Journal",
                "type": "bank",
                "code": "TBNK",
                "company_id": cls.company.id,
            }
        )
        cls.env["account.payment.method.line"].create(
            {
                "name": "SEPA Direct Debit",
                "payment_method_id": cls.payment_method.id,
                "journal_id": cls.journal.id,
            }
        )
        cls.payment_mode = cls.env["account.payment.mode"].create(
            {
                "name": "Direct Debit",
                "payment_method_id": cls.payment_method.id,
                "bank_account_link": "fixed",
                "fixed_journal_id": cls.journal.id,
                "company_id": cls.company.id,
            }
        )
        cls.mandate = cls.env["account.banking.mandate"].create(
            {
                "partner_id": cls.partner.id,
                "partner_bank_id": cls.partner_bank.id,
                "signature_date": fields.Date.today(),
                "company_id": cls.company.id,
                "state": "valid",
            }
        )
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "company_id": cls.company.id,
                "payment_mode_id": cls.payment_mode.id,
            }
        )

    def test_01_mandate_required_related(self):
        self.assertTrue(self.sale_order.mandate_required)

    def test_02_compute_mandate_id(self):
        self.sale_order._compute_mandate_id()
        self.assertEqual(self.sale_order.mandate_id, self.mandate)

    def test_03_prepare_invoice_copies_mandate(self):
        self.sale_order.mandate_id = self.mandate
        vals = self.sale_order._prepare_invoice()
        self.assertEqual(vals.get("mandate_id"), self.mandate.id)

    def test_04_no_mandate_for_other_partner(self):
        other_partner = self.env["res.partner"].create({"name": "Other Partner"})
        self.sale_order.partner_invoice_id = other_partner
        self.sale_order._compute_mandate_id()
        self.assertFalse(self.sale_order.mandate_id)

    def test_05_no_mandate_without_payment_mode(self):
        self.sale_order.payment_mode_id = False
        self.sale_order._compute_mandate_id()
        self.assertFalse(self.sale_order.mandate_id)

    def test_06_onchange_partner_invoice(self):
        self.sale_order.mandate_id = False
        self.sale_order.partner_invoice_id = self.partner
        self.sale_order._compute_mandate_id()
        self.assertEqual(self.sale_order.mandate_id, self.mandate)
