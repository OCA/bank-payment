# Copyright 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# Copyright 2018-2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from lxml import etree

from odoo import fields
from odoo.tools import float_compare

from odoo.addons.account.tests.account_test_multi_company_no_chart import (
    TestAccountMultiCompanyNoChartCommon,
)


class TestSDDBase(TestAccountMultiCompanyNoChartCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        self = cls
        self.company = self.env["res.company"]
        self.account_model = self.env["account.account"]
        self.journal_model = self.env["account.journal"]
        self.payment_order_model = self.env["account.payment.order"]
        self.payment_line_model = self.env["account.payment.line"]
        self.mandate_model = self.env["account.banking.mandate"]
        self.bank_line_model = self.env["bank.payment.line"]
        self.partner_bank_model = self.env["res.partner.bank"]
        self.attachment_model = self.env["ir.attachment"]
        self.invoice_model = self.env["account.move"]
        self.partner_agrolait = self.env.ref("base.res_partner_2")
        self.partner_c2c = self.env.ref("base.res_partner_12")
        self.eur_currency = self.env.ref("base.EUR")
        cls.setUpAdditionalAccounts()
        cls.setUpAccountJournal()
        self.main_company = cls.company_B
        cls.company_B.write(
            {
                "name": "Test EUR company",
                "currency_id": self.eur_currency.id,
                "sepa_creditor_identifier": "FR78ZZZ424242",
            }
        )
        self.env.user.write(
            {
                "company_ids": [(6, 0, self.main_company.ids)],
                "company_id": self.main_company.id,
            }
        )
        (self.partner_agrolait + self.partner_c2c).write(
            {
                "company_id": cls.main_company.id,
                "property_account_payable_id": cls.account_payable_company_B.id,
                "property_account_receivable_id": cls.account_receivable_company_B.id,
            }
        )
        self.company_bank = self.env.ref("account_payment_mode.main_company_iban").copy(
            {
                "company_id": self.main_company.id,
                "partner_id": self.main_company.partner_id.id,
                "bank_id": (
                    self.env.ref("account_payment_mode.bank_la_banque_postale").id
                ),
            }
        )
        # create journal
        self.bank_journal = self.journal_model.create(
            {
                "name": "Company Bank journal",
                "type": "bank",
                "code": "BNKFC",
                "bank_account_id": self.company_bank.id,
                "bank_id": self.company_bank.bank_id.id,
            }
        )
        # update payment mode
        self.payment_mode = self.env.ref(
            "account_banking_sepa_direct_debit.payment_mode_inbound_sepa_dd1"
        ).copy({"company_id": self.main_company.id})
        self.payment_mode.write(
            {"bank_account_link": "fixed", "fixed_journal_id": self.bank_journal.id}
        )
        # Copy partner bank accounts
        bank1 = self.env.ref("account_payment_mode.res_partner_12_iban").copy(
            {"company_id": self.main_company.id}
        )
        self.mandate12 = self.env.ref(
            "account_banking_sepa_direct_debit.res_partner_12_mandate"
        ).copy(
            {
                "partner_bank_id": bank1.id,
                "company_id": self.main_company.id,
                "state": "valid",
                "unique_mandate_reference": "BMTEST12",
            }
        )
        bank2 = self.env.ref("account_payment_mode.res_partner_2_iban").copy(
            {"company_id": self.main_company.id}
        )
        self.mandate2 = self.env.ref(
            "account_banking_sepa_direct_debit.res_partner_2_mandate"
        ).copy(
            {
                "partner_bank_id": bank2.id,
                "company_id": self.main_company.id,
                "state": "valid",
                "unique_mandate_reference": "BMTEST2",
            }
        )
        # Trigger the recompute of account type on res.partner.bank
        self.partner_bank_model.search([])._compute_acc_type()

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
        # Check bank payment line
        bank_lines = self.bank_line_model.search(
            [("partner_id", "=", self.partner_agrolait.id)]
        )
        self.assertEqual(len(bank_lines), 1)
        agrolait_bank_line = bank_lines[0]
        self.assertEqual(agrolait_bank_line.currency_id, self.eur_currency)
        self.assertEqual(
            float_compare(
                agrolait_bank_line.amount_currency, 42.0, precision_digits=accpre
            ),
            0,
        )
        self.assertEqual(agrolait_bank_line.communication_type, "normal")
        self.assertEqual(agrolait_bank_line.communication, invoice1.name)
        self.assertEqual(agrolait_bank_line.mandate_id, invoice1.mandate_id)
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
            self.assertEqual(inv.invoice_payment_state, "paid")
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
                "type": inv_type,
                "date": fields.Date.today(),
                "payment_mode_id": self.payment_mode.id,
                "mandate_id": mandate.id,
                "invoice_line_ids": invoice_vals,
            }
        )
        invoice.post()
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
