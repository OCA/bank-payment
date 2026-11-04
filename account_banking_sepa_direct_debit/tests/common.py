# Copyright 2026 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command, fields, models

from odoo.addons.base.tests.common import BaseCommon


class AccountBankingMandateCommon(BaseCommon):
    _test_user_groups = (
        "base.group_user",
        "base.group_partner_manager",
        "account.group_account_manager",
        "account_payment_order.group_account_payment",
    )

    @classmethod
    def setup_independent_company(cls):
        return cls.env["res.company"].create(
            {
                "name": "SEPA Direct Debit Test Company",
                "currency_id": cls.env.ref("base.EUR").id,
                "sepa_creditor_identifier": "FR78ZZZ424242",
            }
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company.partner_id.company_id = cls.company
        cls.partner_2 = cls.env["res.partner"].create(
            {"name": "Test Partner 2", "company_id": cls.company.id}
        )
        cls.bank_account = cls._create_partner_bank(
            cls.env,
            cls.partner,
            "FR66 1212 1212 1212 1212 1212 121",
            cls.company,
        )
        cls.bank_account_02 = cls._create_partner_bank(
            cls.env,
            cls.partner_2,
            "FR20 1242 1242 1242 1242 1242 124",
            cls.company,
        )
        cls.mandate = cls.env["account.banking.mandate"].create(
            {
                "partner_bank_id": cls.bank_account.id,
                "format": "sepa",
                "type": "oneoff",
                "signature_date": "2015-01-01",
                "company_id": cls.company.id,
            }
        )

    @classmethod
    def _create_partner_bank(
        cls,
        env,
        partner: models.Model,
        account_number: str,
        company: models.Model | None = None,
    ) -> models.Model:
        return env["res.partner.bank"].create(
            {
                "account_number": account_number,
                "bank_name": "Test Bank",
                "bank_bic": "TESTBICXXXX",
                "partner_id": partner.id,
                "company_id": company.id if company else False,
            }
        )


class AccountBankingSepaDirectDebitCommon(AccountBankingMandateCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_B = cls.company
        cls.eur_currency = cls.env.ref("base.EUR")
        cls.account_payable_company_B = cls.env["account.account"].create(
            {
                "code": "NC1110",
                "name": "Test Payable Account Company B",
                "account_type": "liability_payable",
                "reconcile": True,
                "company_ids": [Command.set(cls.company.ids)],
            }
        )
        cls.account_receivable_company_B = cls.env["account.account"].create(
            {
                "code": "NC1111",
                "name": "Test Receivable Account Company B",
                "account_type": "asset_receivable",
                "reconcile": True,
                "company_ids": [Command.set(cls.company.ids)],
            }
        )
        cls.account_income_company_B = cls.env["account.account"].create(
            {
                "code": "NC1112",
                "name": "Sale - Test Account Company B",
                "account_type": "expense_direct_cost",
                "company_ids": [Command.set(cls.company.ids)],
            }
        )
        cls.account_expense_company_B = cls.env["account.account"].create(
            {
                "code": "NC1113",
                "name": "HR Expense - Test Purchase Account Company B",
                "account_type": "expense",
                "company_ids": [Command.set(cls.company.ids)],
                "reconcile": True,
            }
        )
        cls.account_revenue_company_B = cls.env["account.account"].create(
            {
                "code": "NC1114",
                "name": "Sales - Test Account Company B",
                "account_type": "expense_direct_cost",
                "company_ids": [Command.set(cls.company.ids)],
                "reconcile": True,
            }
        )
        cls.journal_purchase_company_B = cls.env["account.journal"].create(
            {
                "name": "Purchase Journal Company B - Test",
                "code": "AJ-PURC",
                "type": "purchase",
                "payment_sequence": False,
                "company_id": cls.company.id,
                "default_account_id": cls.account_expense_company_B.id,
            }
        )
        cls.journal_sale_company_B = cls.env["account.journal"].create(
            {
                "name": "Sale Journal Company B - Test",
                "code": "AJ-SALE",
                "type": "sale",
                "payment_sequence": False,
                "company_id": cls.company.id,
                "default_account_id": cls.account_income_company_B.id,
            }
        )
        cls.journal_general_company_B = cls.env["account.journal"].create(
            {
                "name": "General Journal Company B - Test",
                "code": "AJ-GENERAL",
                "type": "general",
                "payment_sequence": False,
                "company_id": cls.company.id,
            }
        )
        cls.partner_agrolait = cls.env["res.partner"].create(
            {"name": "Agrolait", "company_id": cls.company.id}
        )
        cls.partner_c2c = cls.env["res.partner"].create(
            {"name": "C2C", "company_id": cls.company.id}
        )
        (cls.partner_agrolait | cls.partner_c2c).write(
            {
                "supplier_payment_mode_id": False,
                "customer_payment_mode_id": False,
                "property_account_payable_id": cls.account_payable_company_B.id,
                "property_account_receivable_id": cls.account_receivable_company_B.id,
            }
        )
        cls.company_bank = cls._create_partner_bank(
            cls.env,
            cls.company.partner_id,
            "ES52 0182 2782 5688 3882 1868",
            cls.company,
        )
        cls.company_bank.write(
            {"bank_name": "La Banque Postale", "bank_bic": "PSSTFRPPXXX"}
        )
        cls.bank_journal = cls.env["account.journal"].create(
            {
                "name": "Company Bank journal",
                "type": "bank",
                "code": "BNKFC",
                "payment_sequence": False,
                "bank_account_id": cls.company_bank.id,
                "inbound_payment_method_line_ids": [
                    Command.create(
                        {
                            "payment_method_id": cls.env.ref(
                                "account_banking_sepa_direct_debit.sepa_direct_debit"
                            ).id,
                            "payment_account_id": cls.account_expense_company_B.id,
                        }
                    )
                ],
            }
        )
        cls.company.currency_exchange_journal_id = cls.bank_journal
        cls.payment_mode = cls.env["account.payment.mode"].create(
            {
                "name": "SEPA Direct Debit of customers",
                "company_id": cls.company.id,
                "payment_method_id": cls.env.ref(
                    "account_banking_sepa_direct_debit.sepa_direct_debit"
                ).id,
                "bank_account_link": "fixed",
                "fixed_journal_id": cls.bank_journal.id,
                "sepa_creditor_identifier": False,
            }
        )
        bank1 = cls._create_partner_bank(
            cls.env,
            cls.partner_c2c,
            "FR66 1212 1212 1212 1212 1212 121",
            cls.company,
        )
        cls.mandate12 = cls.env["account.banking.mandate"].create(
            {
                "format": "sepa",
                "type": "recurrent",
                "recurrent_sequence_type": "first",
                "signature_date": fields.Date.to_string(
                    fields.Date.today().replace(month=1, day=1)
                ),
                "partner_bank_id": bank1.id,
                "company_id": cls.company.id,
                "state": "valid",
                "unique_mandate_reference": "BMTEST12",
            }
        )
        bank2 = cls._create_partner_bank(
            cls.env,
            cls.partner_agrolait,
            "BE96 9988 7766 5544",
            cls.company,
        )
        cls.mandate2 = cls.env["account.banking.mandate"].create(
            {
                "format": "sepa",
                "type": "recurrent",
                "recurrent_sequence_type": "first",
                "signature_date": fields.Date.to_string(
                    fields.Date.today().replace(day=1)
                ),
                "partner_bank_id": bank2.id,
                "company_id": cls.company.id,
                "state": "valid",
                "unique_mandate_reference": "BMTEST2",
            }
        )
        cls.payment_order_model = cls.env["account.payment.order"]
        cls.payment_line_model = cls.env["account.payment.line"]
        cls.attachment_model = cls.env["ir.attachment"]
        cls.invoice_model = cls.env["account.move"]
