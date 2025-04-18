# Copyright 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# Copyright 2018-2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from lxml import etree

from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.tools import float_compare

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestSDDBase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.company_B = cls.env["res.company"].create({"name": "Company B"})
        cls.account_payable_company_B = cls.env["account.account"].create(
            {
                "code": "NC1110",
                "name": "Test Payable Account Company B",
                "account_type": "liability_payable",
                "reconcile": True,
                "company_id": cls.company_B.id,
            }
        )
        cls.account_receivable_company_B = cls.env["account.account"].create(
            {
                "code": "NC1111",
                "name": "Test Receivable Account Company B",
                "account_type": "asset_receivable",
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
        cls.partner_agrolait = cls.env["res.partner"].create({"name": "Agrolait"})
        cls.partner_c2c = cls.env["res.partner"].create({"name": "C2C"})
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
                "supplier_payment_mode_id": False,
                "customer_payment_mode_id": False,
                "property_account_payable_id": cls.account_payable_company_B.id,
                "property_account_receivable_id": cls.account_receivable_company_B.id,
            }
        )
        cls.bank = cls.env["res.bank"].create(
            {
                "name": "La Banque Postale",
                "bic": "PSSTFRPPXXX",
                "street": "115 rue de Sèvres",
                "zip": "75007",
                "city": "Paris",
                "country": cls.env.ref("base.fr").id,
            }
        )
        cls.company_bank = cls.env["res.partner.bank"].create(
            {
                "acc_number": "ES52 0182 2782 5688 3882 1868",
                "bank_id": cls.bank.id,
                "partner_id": cls.main_company.partner_id.id,
                "company_id": cls.main_company.id,
            }
        )
        # create journal
        cls.bank_journal = cls.journal_model.create(
            {
                "name": "Company Bank journal",
                "type": "bank",
                "code": "BNKFC",
                "payment_sequence": False,
                "bank_account_id": cls.company_bank.id,
                "bank_id": cls.company_bank.bank_id.id,
                "inbound_payment_method_line_ids": [
                    (
                        0,
                        0,
                        {
                            "payment_method_id": cls.env.ref(
                                "account_banking_sepa_direct_debit.sepa_direct_debit"
                            ).id,
                            "payment_account_id": cls.account_expense_company_B.id,
                        },
                    )
                ],
            }
        )
        # update payment mode
        cls.payment_mode = cls.env["account.payment.mode"].create(
            {
                "name": "SEPA Direct Debit of customers",
                "company_id": cls.main_company.id,
                "payment_method_id": cls.env.ref(
                    "account_banking_sepa_direct_debit.sepa_direct_debit"
                ).id,
                "bank_account_link": "fixed",
                "fixed_journal_id": cls.bank_journal.id,
            }
        )
        # Copy partner bank accounts
        bank1 = cls.env["res.partner.bank"].create(
            {
                "acc_number": "FR66 1212 1212 1212 1212 1212 121",
                "bank_id": cls.bank.id,
                "company_id": cls.main_company.id,
                "partner_id": cls.partner_c2c.id,
                "acc_type": "iban",
            }
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
                "company_id": cls.main_company.id,
                "state": "valid",
                "unique_mandate_reference": "BMTEST12",
            }
        )
        bank2 = cls.env["res.partner.bank"].create(
            {
                "acc_number": "BE96 9988 7766 5544",
                "bank_id": cls.bank.id,
                "company_id": cls.main_company.id,
                "partner_id": cls.partner_agrolait.id,
                "acc_type": "iban",
            }
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
        cls.account_income = cls.env["account.account"].create(
            {
                "code": "NC1112",
                "name": "Sale - Test Account",
                "account_type": "asset_current",
            }
        )
        cls.account_expense = cls.env["account.account"].create(
            {
                "code": "NC1113",
                "name": "HR Expense - Test Purchase Account",
                "account_type": "expense",
            }
        )
        cls.account_revenue = cls.env["account.account"].create(
            {
                "code": "NC1114",
                "name": "Sales - Test Sales Account",
                "account_type": "expense_direct_cost",
                "reconcile": True,
            }
        )
        cls.account_income_company_B = cls.env["account.account"].create(
            {
                "code": "NC1112",
                "name": "Sale - Test Account Company B",
                "account_type": "expense_direct_cost",
                "company_id": cls.company_B.id,
            }
        )
        cls.account_expense_company_B = cls.env["account.account"].create(
            {
                "code": "NC1113",
                "name": "HR Expense - Test Purchase Account Company B",
                "account_type": "expense",
                "company_id": cls.company_B.id,
            }
        )
        cls.account_revenue_company_B = cls.env["account.account"].create(
            {
                "code": "NC1114",
                "name": "Sales - Test Sales Account Company B",
                "account_type": "expense_direct_cost",
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
                "payment_sequence": False,
                "company_id": cls.company_B.id,
                "default_account_id": cls.account_expense_company_B.id,
            }
        )
        cls.journal_sale_company_B = cls.env["account.journal"].create(
            {
                "name": "Sale Journal Company B - Test",
                "code": "AJ-SALE",
                "type": "sale",
                "payment_sequence": False,
                "company_id": cls.company_B.id,
                "default_account_id": cls.account_income_company_B.id,
            }
        )
        cls.journal_general_company_B = cls.env["account.journal"].create(
            {
                "name": "General Journal Company B - Test",
                "code": "AJ-GENERAL",
                "type": "general",
                "payment_sequence": False,
                "company_id": cls.company_B.id,
            }
        )

    def check_sdd(self):
        self.mandate2.recurrent_sequence_type = "first"
        invoice1 = self.create_invoice(self.partner_agrolait.id, self.mandate2, 42.0)
        self.mandate12.type = "oneoff"
        invoice2 = self.create_invoice(self.partner_c2c.id, self.mandate12, 11.0)
        self.payment_mode.payment_method_id.mandate_required = True
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
        payment_order._compute_sepa()
        payment_order.draft2open()
        self.assertEqual(payment_order.state, "open")
        self.assertEqual(payment_order.sepa, True)
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
                "journal_id": self.journal_sale_company_B.id,
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
