# © 2021 DanielDominguez (Xtendoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestSaleMandate(TransactionCase):
    def setUp(self):
        res = super(TestSaleMandate, self).setUp()
        self.company = self.env.ref("base.main_company")
        self.partner = self._create_res_partner("Peter with ACME Bank")
        self.acme_bank = self._create_res_bank(
            "ACME Bank", "GEBABEBB03B", "Charleroi", self.env.ref("base.be")
        )
        bank_account = self.env["res.partner.bank"].create(
            {
                "acc_number": "0023032234211123",
                "partner_id": self.partner.id,
                "bank_id": self.acme_bank.id,
                "company_id": self.company.id,
            }
        )
        self.mandate = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": bank_account.id,
                "signature_date": "2015-01-01",
                "company_id": self.company.id,
            }
        )
        self.mandate.validate()
        self.mode_inbound_acme = self.env["account.payment.mode"].create(
            {
                "name": "Inbound Credit ACME Bank",
                "company_id": self.company.id,
                "bank_account_link": "variable",
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
            }
        )
        bank_journal = self.env["account.journal"].search(
            [("type", "=", "bank")], limit=1
        )
        product = self.env["product.product"].create({"name": "product_test", "invoice_policy": "order"})
        self.mode_inbound_acme.variable_journal_ids = bank_journal
        self.mode_inbound_acme.payment_method_id.mandate_required = True
        self.mode_inbound_acme.payment_order_ok = True
        self.partner.customer_payment_mode_id = self.mode_inbound_acme
        sale_order_vals = [
            (
                0,
                0,
                {
                    "product_id": product.id,
                    "product_uom_qty": 1.0,
                    "price_unit": 200.00,
                },
            )
        ]
        self.sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "company_id": self.company.id,
                "order_line": sale_order_vals,
                "mandate_id": self.mandate.id,
            }
        )

        return res

    def test_sale_order_mandate_partner_id(self):
        self.sale_order.onchange_partner_id()
        self.assertEqual(self.sale_order.mandate_id, self.mandate)
        self.sale_order.action_confirm()
        self.sale_order._create_invoices()
        self.assertEqual(self.sale_order.mandate_id.id, self.sale_order.invoice_ids.mandate_id.id)

    def test_sale_order_without_mandate_on_change_partner_id(self):
        partner_3 = self._create_res_partner("Jane without ACME Bank")
        self.sale_order.partner_id = partner_3.id
        self.sale_order.onchange_partner_id()
        self.sale_order.payment_mode_change()
        self.assertEqual(self.sale_order.mandate_id.id, False)
        self.sale_order.action_confirm()
        self.sale_order._create_invoices()
        self.assertEqual(self.sale_order.mandate_id.id, self.sale_order.invoice_ids.mandate_id.id)

    def test_sale_order_mandate_on_change_partner_id(self):
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
        self.sale_order.partner_id = partner_2.id
        self.sale_order.onchange_partner_id()
        self.sale_order.payment_mode_change()
        self.assertEqual(self.sale_order.mandate_id, mandate_2)
        self.sale_order.action_confirm()
        self.sale_order._create_invoices()
        self.assertEqual(self.sale_order.mandate_id.id, self.sale_order.invoice_ids.mandate_id.id)



    def _create_res_partner(self, name):
        return self.env["res.partner"].create({"name": name})

    def _create_res_bank(self, name, bic, city, country):
        return self.env["res.bank"].create(
            {"name": name, "bic": bic, "city": city, "country": country.id}
        )

