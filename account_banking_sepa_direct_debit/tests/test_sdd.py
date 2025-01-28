# Copyright 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# Copyright 2018-2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from lxml import etree

from odoo import Command
from odoo.tests import tagged
from odoo.tools import float_compare

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestSDDBase(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.eur_currency = cls.env.ref("base.EUR")
        cls.test_company_dict = cls.setup_other_company(
            name="Test EUR company SEPA DD",
            currency_id=cls.eur_currency.id,
            sepa_creditor_identifier="FR78ZZZ424242",
        )
        cls.company = cls.test_company_dict["company"]
        cls.env.user.write(
            {
                "groups_id": [
                    Command.link(
                        cls.env.ref("account_payment_order.group_account_payment").id
                    )
                ],
                "company_ids": [Command.link(cls.company.id)],
            }
        )
        cls.account_model = cls.env["account.account"]
        cls.payment_order_model = cls.env["account.payment.order"]
        cls.payment_line_model = cls.env["account.payment.line"]
        cls.mandate_model = cls.env["account.banking.mandate"]
        cls.partner_model = cls.env["res.partner"]
        cls.partner_bank_model = cls.env["res.partner.bank"]
        cls.mandate_model = cls.env["account.banking.mandate"]
        cls.invoice_model = cls.env["account.move"]
        cls.partner1 = cls.partner_model.create(
            {
                "name": "P1",
                "company_id": cls.company.id,
            }
        )
        cls.partner1_bank = cls.partner_bank_model.create(
            {
                "acc_number": "FR771111 9999 8888 5555 9999 233",
                "partner_id": cls.partner1.id,
            }
        )
        cls.partner2 = cls.partner_model.create(
            {
                "name": "P2",
                "company_id": cls.company.id,
            }
        )
        cls.partner2_bank = cls.partner_bank_model.create(
            {
                "acc_number": "FR891111 9999 8888 5555 9999 987",
                "partner_id": cls.partner2.id,
            }
        )
        cls.company_bank = cls.env["res.partner.bank"].create(
            {
                "company_id": cls.company.id,
                "partner_id": cls.company.partner_id.id,
                "bank_id": (
                    cls.env.ref("account_payment_base_oca.bank_la_banque_postale").id
                ),
                "acc_number": "ES52 0182 2782 5688 3882 1868",
            }
        )
        # create journal
        cls.bank_journal = cls.test_company_dict["default_journal_bank"]
        cls.bank_journal.write({"bank_account_id": cls.company_bank.id})
        cls.payment_account = cls.env["account.account"].create(
            {
                "code": "SEPACTpay",
                "name": "Test SEPA CT Account Company B",
                "account_type": "liability_current",
                "reconcile": True,
                "company_ids": [Command.link(cls.company.id)],
            }
        )

        # create payment mode
        cls.payment_method_line = cls.env["account.payment.method.line"].create(
            {
                "name": "SEPA direct debit test",
                "company_id": cls.company.id,
                "payment_method_id": cls.env.ref(
                    "account_banking_sepa_direct_debit.sepa_direct_debit"
                ).id,
                "bank_account_link": "fixed",
                "journal_id": cls.bank_journal.id,
                "payment_account_id": cls.payment_account.id,
            }
        )
        cls.partner1_mandate = cls.mandate_model.create(
            {
                "partner_bank_id": cls.partner1_bank.id,
                "company_id": cls.company.id,
                "signature_date": "2023-11-05",
                "state": "valid",
                "unique_mandate_reference": "BMTESTP1",
            }
        )
        cls.partner2_mandate = cls.mandate_model.create(
            {
                "partner_bank_id": cls.partner2_bank.id,
                "company_id": cls.company.id,
                "signature_date": "2023-10-05",
                "state": "valid",
                "unique_mandate_reference": "BMTESTP2",
            }
        )

    def check_sdd(self):
        self.partner2_mandate.recurrent_sequence_type = "first"
        invoice1 = self.create_invoice(self.partner1.id, self.partner2_mandate, 42.0)
        self.partner1_mandate.type = "oneoff"
        invoice2 = self.create_invoice(self.partner2.id, self.partner1_mandate, 11.0)
        self.payment_method_line.payment_method_id.mandate_required = True
        for inv in [invoice1, invoice2]:
            action = inv.create_account_payment_line()
        self.assertEqual(action["res_model"], "account.payment.order")
        payment_order = self.payment_order_model.browse(action["res_id"])
        self.assertEqual(payment_order.payment_type, "inbound")
        self.assertEqual(payment_order.payment_method_line_id, self.payment_method_line)
        self.assertEqual(payment_order.journal_id, self.bank_journal)
        # Check payment line
        pay_lines = self.payment_line_model.search(
            [
                ("partner_id", "=", self.partner1.id),
                ("order_id", "=", payment_order.id),
            ]
        )
        self.assertEqual(len(pay_lines), 1)
        partner1_pay_line1 = pay_lines[0]
        accpre = self.env["decimal.precision"].precision_get("Account")
        self.assertEqual(partner1_pay_line1.currency_id, self.eur_currency)
        self.assertEqual(partner1_pay_line1.mandate_id, invoice1.mandate_id)
        self.assertEqual(
            partner1_pay_line1.partner_bank_id, invoice1.mandate_id.partner_bank_id
        )
        self.assertEqual(
            float_compare(
                partner1_pay_line1.amount_currency, 42, precision_digits=accpre
            ),
            0,
        )
        self.assertEqual(partner1_pay_line1.communication_type, "free")
        self.assertEqual(partner1_pay_line1.communication, invoice1.name)
        payment_order._compute_sepa()
        payment_order.draft2open()
        self.assertEqual(payment_order.state, "open")
        self.assertEqual(payment_order.sepa, True)
        # Check account payment
        partner1_bank_line = payment_order.payment_ids[0]
        self.assertEqual(partner1_bank_line.currency_id, self.eur_currency)
        self.assertEqual(
            float_compare(partner1_bank_line.amount, 42.0, precision_digits=accpre),
            0,
        )
        self.assertEqual(partner1_bank_line.payment_reference, invoice1.name)
        self.assertEqual(
            partner1_bank_line.partner_bank_id, invoice1.mandate_id.partner_bank_id
        )
        payment_order.open2generated()
        self.assertEqual(payment_order.state, "generated")
        attachment = payment_order.payment_file_id
        self.assertTrue(attachment)
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
            self.assertIn(inv.payment_state, ("in_payment", "paid"))
        self.assertEqual(self.partner2_mandate.recurrent_sequence_type, "recurring")
        return

    def create_invoice(self, partner_id, mandate, price_unit, inv_type="out_invoice"):
        line_vals = {
            "name": "Great service",
            "quantity": 1,
            "account_id": self.test_company_dict["default_account_revenue"].id,
            "price_unit": price_unit,
        }
        invoice = self.invoice_model.create(
            {
                "partner_id": partner_id,
                "reference_type": "free",
                "currency_id": self.env.ref("base.EUR").id,
                "move_type": inv_type,
                "company_id": self.company.id,
                "preferred_payment_method_line_id": self.payment_method_line.id,
                "mandate_id": mandate.id,
                "invoice_line_ids": [Command.create(line_vals)],
            }
        )
        invoice.action_post()
        return invoice


class TestSDD(TestSDDBase):
    def test_pain_008_001_02(self):
        self.payment_method_line.payment_method_id.pain_version = "pain.008.001.02"
        self.check_sdd()

    def test_pain_0008_001_08(self):
        self.payment_method_line.payment_method_id.pain_version = "pain.008.001.08"
        self.check_sdd()

    def test_pain_008_003_02(self):
        self.payment_method_line.payment_method_id.pain_version = "pain.008.003.02"
        self.check_sdd()
