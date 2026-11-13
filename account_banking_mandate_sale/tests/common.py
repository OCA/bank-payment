# Copyright 2026 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class AccountBankingMandateSaleCommon(AccountTestInvoicingCommon):
    _test_user_groups = (
        "base.group_user",
        "account.group_account_manager",
        "account_payment_order.group_account_payment",
        "sales_team.group_sale_manager",
    )

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.company = cls.env.company
        cls.partner = cls.partner_a
        cls.partner.is_company = True
        cls.payment_method = cls.env["account.payment.method"].create(
            {
                "name": "SEPA Direct Debit",
                "mandate_required": True,
                "payment_type": "inbound",
                "code": "sepa_direct_debit",
            }
        )
        cls.journal = cls.company_data["default_journal_bank"]
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
        cls.mandate = cls._create_mandate(
            "ES9121000418450200051332", "MANDATE-01", "valid"
        )
        cls.sale_order = (
            cls.env["sale.order"]
            .sudo()
            .create(
                {
                    "partner_id": cls.partner.id,
                    "partner_invoice_id": cls.partner.id,
                    "company_id": cls.company.id,
                    "payment_mode_id": cls.payment_mode.id,
                    "order_line": [
                        (0, 0, {"product_id": cls.product_a.id, "product_uom_qty": 1})
                    ],
                }
            )
        )

    @classmethod
    def _create_mandate(
        cls,
        account_number: str,
        reference: str,
        state: str,
        company: models.Model | None = None,
    ) -> models.Model:
        company = company or cls.company
        partner_bank = (
            cls.env["res.partner.bank"]
            .with_company(company)
            .create(
                {
                    "account_number": account_number,
                    "bank_name": "Test Bank",
                    "bank_bic": "TESTBICX",
                    "partner_id": cls.partner.id,
                    "company_id": company.id,
                }
            )
        )
        return (
            cls.env["account.banking.mandate"]
            .with_company(company)
            .sudo()
            .create(
                {
                    "partner_bank_id": partner_bank.id,
                    "unique_mandate_reference": reference,
                    "signature_date": fields.Date.today(),
                    "company_id": company.id,
                    "state": state,
                }
            )
        )
