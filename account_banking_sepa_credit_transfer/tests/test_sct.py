# Copyright 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# Copyright 2020 Sygel Technology - Valentin Vinagre
# Copyright 2018-2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import time

from lxml import etree

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestSCT(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.account_model = cls.env["account.account"]
        cls.move_model = cls.env["account.move"]
        cls.journal_model = cls.env["account.journal"]
        cls.payment_order_model = cls.env["account.payment.order"]
        cls.payment_line_model = cls.env["account.payment.line"]
        cls.partner_model = cls.env["res.partner"]
        cls.partner_bank_model = cls.env["res.partner.bank"]
        cls.invoice_model = cls.env["account.move"]
        cls.invoice_line_model = cls.env["account.move.line"]
        cls.eur_currency = cls.env.ref("base.EUR")
        cls.eur_currency.active = True
        cls.usd_currency = cls.env.ref("base.USD")
        cls.usd_currency.active = True
        cls.main_company = cls.env["res.company"].create(
            {"name": "Test EUR company", "currency_id": cls.eur_currency.id}
        )
        cls.partner1 = cls.partner_model.create(
            {
                "name": "P1",
                "company_id": cls.main_company.id,
            }
        )
        cls.partner1_bank = cls.partner_bank_model.create(
            {
                "acc_number": "FR731111 9999 8888 5555 9999 111",
                "partner_id": cls.partner1.id,
            }
        )
        cls.partner2 = cls.partner_model.create(
            {
                "name": "P2",
                "company_id": cls.main_company.id,
            }
        )
        cls.partner2_bank = cls.partner_bank_model.create(
            {
                "acc_number": "FR831111 9999 8888 5555 9999 222",
                "partner_id": cls.partner2.id,
            }
        )
        cls.partner3 = cls.partner_model.create(
            {
                "name": "P3",
                "company_id": cls.main_company.id,
            }
        )
        cls.partner3_bank = cls.partner_bank_model.create(
            {
                "acc_number": "FR931111 9999 8888 5555 9999 333",
                "partner_id": cls.partner3.id,
            }
        )
        cls.account_expense = cls.account_model.create(
            {
                "account_type": "expense",
                "company_id": cls.main_company.id,
                "name": "Test expense",
                "code": "TE.1",
            }
        )
        cls.account_payable = cls.account_model.create(
            {
                "account_type": "liability_payable",
                "company_id": cls.main_company.id,
                "name": "Test payable",
                "code": "TP.1",
            }
        )
        (cls.partner1 + cls.partner2 + cls.partner3).with_company(
            cls.main_company.id
        ).write({"property_account_payable_id": cls.account_payable.id})
        cls.general_journal = cls.journal_model.create(
            {
                "name": "General journal",
                "type": "general",
                "code": "GEN",
                "company_id": cls.main_company.id,
            }
        )
        cls.purchase_journal = cls.journal_model.create(
            {
                "name": "Purchase journal",
                "type": "purchase",
                "code": "PUR",
                "company_id": cls.main_company.id,
            }
        )

        cls.partner_bank = cls.partner_bank_model.create(
            {
                "acc_number": "FR0812221333144415551666777",
                "company_id": cls.main_company.id,
                "partner_id": cls.main_company.partner_id.id,
                "bank_id": (
                    cls.env.ref("account_payment_mode.bank_la_banque_postale").id
                ),
            }
        )
        cls.bank_journal = cls.journal_model.create(
            {
                "name": "Company Bank journal",
                "type": "bank",
                "code": "BNKFB",
                "bank_account_id": cls.partner_bank.id,
                "bank_id": cls.partner_bank.bank_id.id,
                "company_id": cls.main_company.id,
                "outbound_payment_method_line_ids": [
                    Command.create(
                        {
                            "payment_method_id": cls.env.ref(
                                "account_banking_sepa_credit_transfer.sepa_credit_transfer"
                            ).id,
                            "payment_account_id": cls.account_expense.id,
                        },
                    )
                ],
            }
        )

        # update payment mode
        cls.payment_mode = cls.env["account.payment.mode"].create(
            {
                "name": "SEPA credit transfer test",
                "company_id": cls.main_company.id,
                "payment_method_id": cls.env.ref(
                    "account_banking_sepa_credit_transfer.sepa_credit_transfer"
                ).id,
                "bank_account_link": "fixed",
                "fixed_journal_id": cls.bank_journal.id,
            }
        )

    def test_no_pain(self):
        self.payment_mode.payment_method_id.pain_version = False
        with self.assertRaises(UserError):
            self.check_eur_currency_sct()

    def test_pain_001_03(self):
        self.payment_mode.payment_method_id.pain_version = "pain.001.001.03"
        self.check_eur_currency_sct()

    def test_pain_001_04(self):
        self.payment_mode.payment_method_id.pain_version = "pain.001.001.04"
        self.check_eur_currency_sct()

    def test_pain_001_05(self):
        self.payment_mode.payment_method_id.pain_version = "pain.001.001.05"
        self.check_eur_currency_sct()

    def test_pain_003_03(self):
        self.payment_mode.payment_method_id.pain_version = "pain.001.003.03"
        self.check_eur_currency_sct()

    def check_eur_currency_sct(self):
        invoice1 = self.create_invoice(
            self.partner1.id,
            "account_payment_mode.res_partner_2_iban",
            self.eur_currency.id,
            42.0,
            "F1341",
        )
        invoice2 = self.create_invoice(
            self.partner1.id,
            "account_payment_mode.res_partner_2_iban",
            self.eur_currency.id,
            12.0,
            "F1342",
        )
        invoice3 = self.create_invoice(
            self.partner1.id,
            "account_payment_mode.res_partner_2_iban",
            self.eur_currency.id,
            5.0,
            "A1301",
            "in_refund",
        )
        invoice4 = self.create_invoice(
            self.partner3.id,
            "account_payment_mode.res_partner_12_iban",
            self.eur_currency.id,
            11.0,
            "I1642",
        )
        invoice5 = self.create_invoice(
            self.partner3.id,
            "account_payment_mode.res_partner_12_iban",
            self.eur_currency.id,
            41.0,
            "I1643",
        )
        for inv in [invoice1, invoice2, invoice3, invoice4, invoice5]:
            action = inv.create_account_payment_line()
        self.assertEqual(action["res_model"], "account.payment.order")
        self.payment_order = self.payment_order_model.browse(action["res_id"])
        self.assertEqual(self.payment_order.payment_type, "outbound")
        self.assertEqual(self.payment_order.payment_mode_id, self.payment_mode)
        self.assertEqual(self.payment_order.journal_id, self.bank_journal)
        pay_lines = self.payment_line_model.search(
            [
                ("partner_id", "=", self.partner1.id),
                ("order_id", "=", self.payment_order.id),
            ]
        )
        self.assertEqual(len(pay_lines), 3)
        partner1_pay_line1 = pay_lines[0]
        self.assertEqual(partner1_pay_line1.currency_id, self.eur_currency)
        self.assertEqual(partner1_pay_line1.partner_bank_id, invoice1.partner_bank_id)
        self.assertEqual(
            partner1_pay_line1.currency_id.compare_amounts(
                partner1_pay_line1.amount_currency, 42
            ),
            0,
        )
        self.assertEqual(partner1_pay_line1.communication_type, "normal")
        self.assertEqual(partner1_pay_line1.communication, "F1341")
        self.payment_order.draft2open()
        self.assertEqual(self.payment_order.state, "open")
        if self.payment_mode.payment_method_id.pain_version:
            self.assertTrue(self.payment_order.sepa)
        else:
            self.assertFalse(self.payment_order.sepa)
        self.assertTrue(self.payment_order.payment_ids)
        partner1_bank_line = self.payment_order.payment_ids[0]
        self.assertEqual(partner1_bank_line.currency_id, self.eur_currency)
        self.assertEqual(
            partner1_bank_line.currency_id.compare_amounts(
                partner1_bank_line.amount, 49.0
            ),
            0,
        )
        self.assertEqual(partner1_bank_line.payment_reference, "F1341 - F1342 - A1301")
        self.assertEqual(partner1_bank_line.partner_bank_id, invoice1.partner_bank_id)

        self.payment_order.open2generated()
        self.assertEqual(self.payment_order.state, "generated")
        attachment = self.payment_order.payment_file_id
        self.assertTrue(attachment)
        self.assertEqual(attachment.name[-4:], ".xml")
        xml_file = base64.b64decode(attachment.datas)
        xml_root = etree.fromstring(xml_file)
        namespaces = xml_root.nsmap
        namespaces["p"] = xml_root.nsmap[None]
        namespaces.pop(None)
        pay_method_xpath = xml_root.xpath("//p:PmtInf/p:PmtMtd", namespaces=namespaces)
        self.assertEqual(pay_method_xpath[0].text, "TRF")
        sepa_xpath = xml_root.xpath(
            "//p:PmtInf/p:PmtTpInf/p:SvcLvl/p:Cd", namespaces=namespaces
        )
        self.assertEqual(sepa_xpath[0].text, "SEPA")
        debtor_acc_xpath = xml_root.xpath(
            "//p:PmtInf/p:DbtrAcct/p:Id/p:IBAN", namespaces=namespaces
        )
        self.assertEqual(
            debtor_acc_xpath[0].text,
            self.payment_order.company_partner_bank_id.sanitized_acc_number,
        )
        self.payment_order.generated2uploaded()
        self.assertEqual(self.payment_order.state, "uploaded")
        for inv in [invoice1, invoice2, invoice3, invoice4, invoice5]:
            self.assertEqual(inv.state, "posted")
            self.assertEqual(
                inv.currency_id.compare_amounts(inv.amount_residual, 0.0),
                0,
            )
        return

    def test_usd_currency_sct(self):
        invoice1 = self.create_invoice(
            self.partner2.id,
            "account_payment_mode.res_partner_2_iban",
            self.usd_currency.id,
            2042.0,
            "Inv9032",
        )
        invoice2 = self.create_invoice(
            self.partner2.id,
            "account_payment_mode.res_partner_2_iban",
            self.usd_currency.id,
            1012.0,
            "Inv9033",
        )
        for inv in [invoice1, invoice2]:
            action = inv.create_account_payment_line()
        self.assertEqual(action["res_model"], "account.payment.order")
        self.payment_order = self.payment_order_model.browse(action["res_id"])
        self.assertEqual(self.payment_order.payment_type, "outbound")
        self.assertEqual(self.payment_order.payment_mode_id, self.payment_mode)
        self.assertEqual(self.payment_order.journal_id, self.bank_journal)
        pay_lines = self.payment_line_model.search(
            [
                ("partner_id", "=", self.partner2.id),
                ("order_id", "=", self.payment_order.id),
            ]
        )
        self.assertEqual(len(pay_lines), 2)
        partner2_pay_line1 = pay_lines[0]
        self.assertEqual(partner2_pay_line1.currency_id, self.usd_currency)
        self.assertEqual(partner2_pay_line1.partner_bank_id, invoice1.partner_bank_id)
        self.assertEqual(
            partner2_pay_line1.currency_id.compare_amounts(
                partner2_pay_line1.amount_currency, 2042
            ),
            0,
        )
        self.assertEqual(partner2_pay_line1.communication_type, "normal")
        self.assertEqual(partner2_pay_line1.communication, "Inv9032")
        self.payment_order.draft2open()
        self.assertEqual(self.payment_order.state, "open")
        self.assertEqual(self.payment_order.sepa, False)
        self.assertEqual(self.payment_order.payment_count, 1)
        partner2_bank_line = self.payment_order.payment_ids[0]
        self.assertEqual(partner2_bank_line.currency_id, self.usd_currency)
        self.assertEqual(
            partner2_bank_line.currency_id.compare_amounts(
                partner2_bank_line.amount, 3054.0
            ),
            0,
        )
        self.assertEqual(partner2_bank_line.payment_reference, "Inv9032 - Inv9033")
        self.assertEqual(partner2_bank_line.partner_bank_id, invoice1.partner_bank_id)

        self.payment_order.open2generated()
        self.assertEqual(self.payment_order.state, "generated")
        attachment = self.payment_order.payment_file_id
        self.assertTrue(attachment)
        self.assertEqual(attachment.name[-4:], ".xml")
        xml_file = base64.b64decode(attachment.datas)
        xml_root = etree.fromstring(xml_file)
        namespaces = xml_root.nsmap
        namespaces["p"] = xml_root.nsmap[None]
        namespaces.pop(None)
        pay_method_xpath = xml_root.xpath("//p:PmtInf/p:PmtMtd", namespaces=namespaces)
        self.assertEqual(pay_method_xpath[0].text, "TRF")
        sepa_xpath = xml_root.xpath(
            "//p:PmtInf/p:PmtTpInf/p:SvcLvl/p:Cd", namespaces=namespaces
        )
        self.assertEqual(len(sepa_xpath), 0)
        debtor_acc_xpath = xml_root.xpath(
            "//p:PmtInf/p:DbtrAcct/p:Id/p:IBAN", namespaces=namespaces
        )
        self.assertEqual(
            debtor_acc_xpath[0].text,
            self.payment_order.company_partner_bank_id.sanitized_acc_number,
        )
        self.payment_order.generated2uploaded()
        self.assertEqual(self.payment_order.state, "uploaded")
        for inv in [invoice1, invoice2]:
            self.assertEqual(inv.state, "posted")
            self.assertEqual(
                inv.currency_id.compare_amounts(inv.amount_residual, 0.0),
                0,
            )
        return

    @classmethod
    def create_invoice(
        cls,
        partner_id,
        partner_bank_xmlid,
        currency_id,
        price_unit,
        reference,
        move_type="in_invoice",
    ):
        partner_bank = cls.env.ref(partner_bank_xmlid)
        partner_bank.write({"company_id": False})
        line_data = {
            "name": "Great service",
            "account_id": cls.account_expense.id,
            "price_unit": price_unit,
            "quantity": 1,
        }
        data = {
            "partner_id": partner_id,
            "reference_type": "none",
            "ref": reference,
            "currency_id": currency_id,
            "invoice_date": time.strftime("%Y-%m-%d"),
            "move_type": move_type,
            "payment_mode_id": cls.payment_mode.id,
            "partner_bank_id": partner_bank.id,
            "company_id": cls.main_company.id,
            "invoice_line_ids": [Command.create(line_data)],
        }
        inv = cls.env["account.move"].create(data)
        inv.action_post()
        return inv
