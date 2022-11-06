# Copyright 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# Copyright 2018-2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from lxml import etree

from odoo import fields
from odoo.tests.common import SavepointCase
from odoo.tools import float_compare


class TestSDDBase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_B = cls.env["res.company"].create({"name": "Company B"})
        user_type_payable = cls.env.ref("account.data_account_type_payable")
        cls.account_payable_company_B = cls.env["account.account"].create(
            {
                "code": "NC1110",
                "name": "Test Payable Account Company B",
                "user_type_id": user_type_payable.id,
                "reconcile": True,
                "company_id": cls.company_B.id,
            }
        )
        user_type_receivable = cls.env.ref("account.data_account_type_receivable")
        cls.account_receivable_company_B = cls.env["account.account"].create(
            {
                "code": "NC1111",
                "name": "Test Receivable Account Company B",
                "user_type_id": user_type_receivable.id,
                "reconcile": True,
                "company_id": cls.company_B.id,
            }
        )
        cls.company = cls.env["res.company"]
        cls.account_model = cls.env["account.account"]
        cls.journal_model = cls.env["account.journal"]
        cls.payment_order_model = cls.env["account.payment.order"]
        cls.payment_line_model = cls.env["account.payment.line"]
        cls.mandate_model = cls.env["account.banking.mandate"]
        cls.partner_bank_model = cls.env["res.partner.bank"]
        cls.attachment_model = cls.env["ir.attachment"]
        cls.invoice_model = cls.env["account.move"]
        cls.partner_agrolait = cls.env.ref("base.res_partner_2")
        cls.partner_c2c = cls.env.ref("base.res_partner_12")
        cls.eur_currency = cls.env.ref("base.EUR")
        cls.setUpAdditionalAccounts()
        cls.setUpAccountJournal()
        cls.main_company = cls.company_B
        cls.company_B.write(
            {
                "name": "Test EUR company",
                "currency_id": cls.eur_currency.id,
                "sepa_creditor_identifier": "FR78ZZZ424242",
            }
        )
        cls.env.user.write(
            {
                "company_ids": [(6, 0, cls.main_company.ids)],
                "company_id": cls.main_company.id,
            }
        )
        (cls.partner_agrolait + cls.partner_c2c).write(
            {
                "company_id": cls.main_company.id,
                "property_account_payable_id": cls.account_payable_company_B.id,
                "property_account_receivable_id": cls.account_receivable_company_B.id,
            }
        )
        cls.company_bank = cls.env.ref("account_payment_mode.main_company_iban").copy(
            {
                "company_id": cls.main_company.id,
                "partner_id": cls.main_company.partner_id.id,
                "bank_id": (
                    cls.env.ref("account_payment_mode.bank_la_banque_postale").id
                ),
            }
        )
        # create journal
        cls.bank_journal = cls.journal_model.create(
            {
                "name": "Company Bank journal",
                "type": "bank",
                "code": "BNKFC",
                "bank_account_id": cls.company_bank.id,
                "bank_id": cls.company_bank.bank_id.id,
            }
        )
        # update payment mode
        cls.payment_mode = cls.env.ref(
            "account_banking_sepa_direct_debit.payment_mode_inbound_sepa_dd1"
        ).copy({"company_id": cls.main_company.id})
        cls.payment_mode.write(
            {"bank_account_link": "fixed", "fixed_journal_id": cls.bank_journal.id}
        )
        # Copy partner bank accounts
        bank1 = cls.env.ref("account_payment_mode.res_partner_12_iban").copy(
            {"company_id": cls.main_company.id}
        )
        cls.mandate12 = cls.env.ref(
            "account_banking_sepa_direct_debit.res_partner_12_mandate"
        ).copy(
            {
                "partner_bank_id": bank1.id,
                "company_id": cls.main_company.id,
                "state": "valid",
                "unique_mandate_reference": "BMTEST12",
            }
        )
        bank2 = cls.env.ref("account_payment_mode.res_partner_2_iban").copy(
            {"company_id": cls.main_company.id}
        )
        cls.mandate2 = cls.env.ref(
            "account_banking_sepa_direct_debit.res_partner_2_mandate"
        ).copy(
            {
                "partner_bank_id": bank2.id,
                "company_id": cls.main_company.id,
                "state": "valid",
                "unique_mandate_reference": "BMTEST2",
            }
        )
        # Trigger the recompute of account type on res.partner.bank
        cls.partner_bank_model.search([])._compute_acc_type()

    @classmethod
    def setUpAdditionalAccounts(cls):
        """Set up some addionnal accounts: expenses, revenue, ..."""
        user_type_income = cls.env.ref("account.data_account_type_direct_costs")
        cls.account_income = cls.env["account.account"].create(
            {
                "code": "NC1112",
                "name": "Sale - Test Account",
                "user_type_id": user_type_income.id,
            }
        )
        user_type_expense = cls.env.ref("account.data_account_type_expenses")
        cls.account_expense = cls.env["account.account"].create(
            {
                "code": "NC1113",
                "name": "HR Expense - Test Purchase Account",
                "user_type_id": user_type_expense.id,
            }
        )
        user_type_revenue = cls.env.ref("account.data_account_type_revenue")
        cls.account_revenue = cls.env["account.account"].create(
            {
                "code": "NC1114",
                "name": "Sales - Test Sales Account",
                "user_type_id": user_type_revenue.id,
                "reconcile": True,
            }
        )
        user_type_income = cls.env.ref("account.data_account_type_direct_costs")
        cls.account_income_company_B = cls.env["account.account"].create(
            {
                "code": "NC1112",
                "name": "Sale - Test Account Company B",
                "user_type_id": user_type_income.id,
                "company_id": cls.company_B.id,
            }
        )
        user_type_expense = cls.env.ref("account.data_account_type_expenses")
        cls.account_expense_company_B = cls.env["account.account"].create(
            {
                "code": "NC1113",
                "name": "HR Expense - Test Purchase Account Company B",
                "user_type_id": user_type_expense.id,
                "company_id": cls.company_B.id,
            }
        )
        user_type_revenue = cls.env.ref("account.data_account_type_revenue")
        cls.account_revenue_company_B = cls.env["account.account"].create(
            {
                "code": "NC1114",
                "name": "Sales - Test Sales Account Company B",
                "user_type_id": user_type_revenue.id,
                "reconcile": True,
                "company_id": cls.company_B.id,
            }
        )

    @classmethod
    def setUpAccountJournal(cls):
        # Set up some journals
        cls.journal_purchase_company_B = cls.env["account.journal"].create(
            {
                "name": "Purchase Journal Company B - Test",
                "code": "AJ-PURC",
                "type": "purchase",
                "company_id": cls.company_B.id,
                "payment_debit_account_id": cls.account_expense_company_B.id,
                "payment_credit_account_id": cls.account_expense_company_B.id,
            }
        )
        cls.journal_sale_company_B = cls.env["account.journal"].create(
            {
                "name": "Sale Journal Company B - Test",
                "code": "AJ-SALE",
                "type": "sale",
                "company_id": cls.company_B.id,
                "payment_debit_account_id": cls.account_income_company_B.id,
                "payment_credit_account_id": cls.account_income_company_B.id,
            }
        )
        cls.journal_general_company_B = cls.env["account.journal"].create(
            {
                "name": "General Journal Company B - Test",
                "code": "AJ-GENERAL",
                "type": "general",
                "company_id": cls.company_B.id,
            }
        )

    def check_sdd(self):
        self.mandate2.recurrent_sequence_type = "first"
        invoice1 = self.create_invoice(self.partner_agrolait.id, self.mandate2, 42.0)
        self.mandate12.type = "oneoff"
        invoice2 = self.create_invoice(self.partner_c2c.id, self.mandate12, 11.0)
        for inv in [invoice1, invoice2]:
            action = inv.create_account_payment_line()
        self.assertEqual(action["res_model"], "account.payment.order")
        payment_order = self.payment_order_model.browse(action["res_id"])
        self.assertEqual(payment_order.payment_type, "inbound")
        self.assertEqual(payment_order.payment_mode_id, self.payment_mode)
        self.assertEqual(payment_order.journal_id, self.bank_journal)
        # Check payment line
        pay_lines = self.payment_line_model.search(
            [
                ("partner_id", "=", self.partner_agrolait.id),
                ("order_id", "=", payment_order.id),
            ]
        )
        self.assertEqual(len(pay_lines), 1)
        agrolait_pay_line1 = pay_lines[0]
        accpre = self.env["decimal.precision"].precision_get("Account")
        self.assertEqual(agrolait_pay_line1.currency_id, self.eur_currency)
        self.assertEqual(agrolait_pay_line1.mandate_id, invoice1.mandate_id)
        self.assertEqual(
            agrolait_pay_line1.partner_bank_id, invoice1.mandate_id.partner_bank_id
        )
        self.assertEqual(
            float_compare(
                agrolait_pay_line1.amount_currency, 42, precision_digits=accpre
            ),
            0,
        )
        self.assertEqual(agrolait_pay_line1.communication_type, "normal")
        self.assertEqual(agrolait_pay_line1.communication, invoice1.name)
        payment_order.draft2open()
        self.assertEqual(payment_order.state, "open")
        self.assertEqual(payment_order.sepa, True)
        # Check account payment
        agrolait_bank_line = payment_order.payment_ids[0]
        self.assertEqual(agrolait_bank_line.currency_id, self.eur_currency)
        self.assertEqual(
            float_compare(agrolait_bank_line.amount, 42.0, precision_digits=accpre),
            0,
        )
        self.assertEqual(agrolait_bank_line.payment_reference, invoice1.name)
        self.assertEqual(
            agrolait_bank_line.partner_bank_id, invoice1.mandate_id.partner_bank_id
        )
        action = payment_order.open2generated()
        self.assertEqual(payment_order.state, "generated")
        self.assertEqual(action["res_model"], "ir.attachment")
        attachment = self.attachment_model.browse(action["res_id"])
        self.assertEqual(attachment.name[-4:], ".xml")
        xml_file = base64.b64decode(attachment.datas)
        xml_root = etree.fromstring(xml_file)
        namespaces = xml_root.nsmap
        namespaces["p"] = xml_root.nsmap[None]
        namespaces.pop(None)
        pay_method_xpath = xml_root.xpath("//p:PmtInf/p:PmtMtd", namespaces=namespaces)
        self.assertEqual(pay_method_xpath[0].text, "DD")
        sepa_xpath = xml_root.xpath(
            "//p:PmtInf/p:PmtTpInf/p:SvcLvl/p:Cd", namespaces=namespaces
        )
        self.assertEqual(sepa_xpath[0].text, "SEPA")
        debtor_acc_xpath = xml_root.xpath(
            "//p:PmtInf/p:CdtrAcct/p:Id/p:IBAN", namespaces=namespaces
        )
        self.assertEqual(
            debtor_acc_xpath[0].text,
            payment_order.company_partner_bank_id.sanitized_acc_number,
        )
        payment_order.generated2uploaded()
        self.assertEqual(payment_order.state, "uploaded")
        for inv in [invoice1, invoice2]:
            self.assertEqual(inv.payment_state, "paid")
        self.assertEqual(self.mandate2.recurrent_sequence_type, "recurring")
        return

    def create_invoice(self, partner_id, mandate, price_unit, inv_type="out_invoice"):
        invoice_vals = [
            (
                0,
                0,
                {
                    "name": "Great service",
                    "quantity": 1,
                    "account_id": self.account_revenue_company_B.id,
                    "price_unit": price_unit,
                },
            )
        ]
        invoice = self.invoice_model.create(
            {
                "partner_id": partner_id,
                "reference_type": "none",
                "currency_id": self.env.ref("base.EUR").id,
                "move_type": inv_type,
                "date": fields.Date.today(),
                "payment_mode_id": self.payment_mode.id,
                "mandate_id": mandate.id,
                "invoice_line_ids": invoice_vals,
            }
        )
        invoice.action_post()
        return invoice


class TestSDD(TestSDDBase):
    def test_pain_001_02(self):
        self.payment_mode.payment_method_id.pain_version = "pain.008.001.02"
        self.check_sdd()

    def test_pain_003_02(self):
        self.payment_mode.payment_method_id.pain_version = "pain.008.003.02"
        self.check_sdd()

    def test_pain_001_03(self):
        self.payment_mode.payment_method_id.pain_version = "pain.008.001.03"
        self.check_sdd()

    def test_pain_001_04(self):
        self.payment_mode.payment_method_id.pain_version = "pain.008.001.04"
        self.check_sdd()
