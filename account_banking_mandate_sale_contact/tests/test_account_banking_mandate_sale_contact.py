# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo import fields
from odoo.tests.common import Form, TransactionCase

from odoo.addons.account.models.account_payment_method import AccountPaymentMethod


class TestAccountBankingMandateSaleContact(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_company = cls.env["res.partner"].create(
            {
                "name": "Test Partner Company",
                "company_type": "company",
            }
        )
        cls.partner_invoice = cls.env["res.partner"].create(
            {
                "name": "Test Partner Invoice Address",
                "company_type": "person",
                "type": "invoice",
                "parent_id": cls.partner_company.id,
            }
        )
        cls.partner_delivery = cls.env["res.partner"].create(
            {
                "name": "Test Partner Delivery Address",
                "company_type": "person",
                "type": "delivery",
                "parent_id": cls.partner_company.id,
            }
        )

        cls.partner_bank = cls._create_res_partner_bank(
            cls.partner_company, "Test Bank"
        )
        cls.mandate_first = cls._create_mandate(cls.partner_bank, "Test Mandate")
        cls.mandate_company = cls._create_mandate(
            cls.partner_bank, "Test Company Mandate"
        )
        cls.mandate_invoice = cls._create_mandate(
            cls.partner_bank, "Test Invoice Mandate"
        )
        cls.mandate_delivery = cls._create_mandate(
            cls.partner_bank, "Test Delivery Mandate"
        )
        cls.payment_method = cls._create_payment_method(
            {
                "name": "Test Payment Method",
                "code": "test_payment_method",
                "payment_type": "inbound",
                "bank_account_required": True,
                "mandate_required": True,
            }
        )
        cls.journal_bank = cls.env["account.journal"].create(
            {"name": "Test Journal", "type": "bank", "code": "bank"}
        )
        payment_form = Form(cls.env["account.payment.mode"])
        payment_form.name = "Test Payment Mode"
        payment_form.payment_method_id = cls.payment_method
        payment_form.bank_account_link = "fixed"
        payment_form.fixed_journal_id = cls.journal_bank
        payment_form.payment_order_ok = True
        cls.payment_mode = payment_form.save()
        cls.partner_company.update(
            {
                "customer_payment_mode_id": cls.payment_mode.id,
                "contact_mandate_id": cls.mandate_company.id,
            }
        )
        cls.partner_invoice.contact_mandate_id = cls.mandate_invoice
        cls.partner_delivery.contact_mandate_id = cls.mandate_delivery

    @classmethod
    def _create_res_partner_bank(cls, partner_id, acc_number):
        res_partner_bank_form = Form(cls.env["res.partner.bank"])
        res_partner_bank_form.partner_id = partner_id
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
    def _create_payment_method(cls, payment_method_vals):
        method_get_payment_method_information = (
            AccountPaymentMethod._get_payment_method_information
        )

        def _get_payment_method_information(cls):
            res = method_get_payment_method_information(cls)
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
            return cls.env["account.payment.method"].create(payment_method_vals)

    def test_sale_mandate(self):
        """Tests the computed sale mandate with the default company configuration"""
        sale_form = Form(self.env["sale.order"].with_context())
        sale_form.partner_id = self.partner_company
        sale = sale_form.save()
        self.assertEqual(sale.mandate_id, self.mandate_company)

    def test_sale_mandate_before(self):
        """Tests the default sale mendate before this module, the first mandate found"""
        self.env.user.company_id.sale_default_mandate_contact = False
        sale_form = Form(self.env["sale.order"].with_context())
        sale_form.partner_id = self.partner_company
        sale = sale_form.save()
        self.assertEqual(sale.mandate_id, self.mandate_first)

    def test_sale_mandate_invoice_address(self):
        """Tests the computed sale mendate with a config based on invoice address"""
        self.partner_company.sale_default_mandate_contact = "partner_invoice_id"
        sale_form = Form(self.env["sale.order"].with_context())
        sale_form.partner_id = self.partner_company
        sale = sale_form.save()
        self.assertEqual(sale.mandate_id, self.mandate_invoice)

    def test_sale_mandate_delivery_address(self):
        """Tests the computed sale mendate with a config based on delivery address"""
        self.partner_company.sale_default_mandate_contact = "partner_shipping_id"
        sale_form = Form(self.env["sale.order"].with_context())
        sale_form.partner_id = self.partner_company
        sale = sale_form.save()
        self.assertEqual(sale.mandate_id, self.mandate_delivery)

    def test_sale_mandate_commercial_partner(self):
        """Tests the computed sale mendate with a config based on delivery address"""
        self.partner_company.sale_default_mandate_contact = "commercial_partner_id"
        sale_form = Form(self.env["sale.order"].with_context())
        sale_form.partner_id = self.partner_invoice
        sale = sale_form.save()
        self.assertEqual(sale.mandate_id, self.mandate_company)
