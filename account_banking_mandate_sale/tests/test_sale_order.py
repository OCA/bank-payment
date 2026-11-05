# Copyright 2025 Studio73 - Eugenio Micó <eugenio@studio73.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form, new_test_user

from .common import AccountBankingMandateSaleCommon


class TestSaleOrder(AccountBankingMandateSaleCommon):
    def test_01_mandate_required_related(self):
        self.assertTrue(self.sale_order.mandate_required)

    def test_02_compute_mandate_id(self):
        self.sale_order._compute_mandate_id()
        self.assertEqual(self.sale_order.mandate_id, self.mandate)

    def test_03_prepare_invoice_copies_mandate(self):
        second_mandate = self._create_mandate(
            "ES9121000418450200051333", "MANDATE-02", "valid"
        )
        self.sale_order.mandate_id = second_mandate
        self.sale_order.action_confirm()
        invoice = self.sale_order._create_invoices()
        self.assertEqual(len(invoice), 1)
        self.assertEqual(invoice.mandate_id, second_mandate)

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

    def test_07_child_invoice_partner_can_select_draft_mandate(self) -> None:
        invoice_contact = self.env["res.partner"].create(
            {
                "name": "Invoice Contact",
                "parent_id": self.partner.id,
                "type": "invoice",
            }
        )
        draft_mandate = self._create_mandate(
            "ES9121000418450200051334", "MANDATE-DRAFT", "draft"
        )
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": invoice_contact.id,
                "company_id": self.company.id,
                "payment_mode_id": self.payment_mode.id,
            }
        )
        self.assertEqual(sale_order.mandate_id, self.mandate)
        with Form(sale_order) as sale_order_form:
            sale_order_form.mandate_id = draft_mandate
        sale_order = sale_order_form.save()
        self.assertEqual(sale_order.mandate_id, draft_mandate)

    def test_08_sales_user_can_edit_orders_in_both_companies(self) -> None:
        company_2_data = self.setup_other_company()
        company_2 = company_2_data["company"]
        company_2.partner_id.company_id = company_2.id
        journal_2 = company_2_data["default_journal_bank"]
        self.env["account.payment.method.line"].create(
            {
                "name": "SEPA Direct Debit",
                "payment_method_id": self.payment_method.id,
                "journal_id": journal_2.id,
            }
        )
        payment_mode_2 = (
            self.env["account.payment.mode"]
            .sudo()
            .create(
                {
                    "name": "Direct Debit Company 2",
                    "payment_method_id": self.payment_method.id,
                    "bank_account_link": "fixed",
                    "fixed_journal_id": journal_2.id,
                    "company_id": company_2.id,
                }
            )
        )
        mandate_2 = self._create_mandate(
            "FR7612345678901234567890123",
            "MANDATE-COMPANY-2",
            "valid",
            company_2,
        )
        user = new_test_user(
            self.env,
            name="Sales User with Two Companies",
            login="mandate_sale_multicompany",
            email="mandate_sale_multicompany@example.com",
            group_ids=[
                self.env.ref("base.group_user").id,
                self.env.ref("account.group_account_user").id,
                self.env.ref("sales_team.group_sale_salesman_all_leads").id,
                self.env.ref("account_payment_order.group_account_payment").id,
            ],
            company_id=self.company.id,
            company_ids=[self.company.id, company_2.id],
        )
        orders = [
            (
                self.env["sale.order"]
                .sudo()
                .with_company(self.company)
                .create(
                    {
                        "partner_id": self.partner.id,
                        "partner_invoice_id": self.partner.id,
                        "company_id": self.company.id,
                        "payment_mode_id": self.payment_mode.id,
                    }
                ),
                self.company,
                self.mandate,
            ),
            (
                self.env["sale.order"]
                .sudo()
                .with_company(company_2)
                .create(
                    {
                        "partner_id": self.partner.id,
                        "partner_invoice_id": self.partner.id,
                        "company_id": company_2.id,
                        "payment_mode_id": payment_mode_2.id,
                    }
                ),
                company_2,
                mandate_2,
            ),
        ]
        for sale_order, company, expected_mandate in orders:
            sale_order = sale_order.with_user(user).with_company(company)
            self.assertEqual(sale_order.mandate_id, expected_mandate)
            sale_order.write({"client_order_ref": "edited by sales user"})
            self.assertEqual(sale_order.mandate_id.company_id, company)
