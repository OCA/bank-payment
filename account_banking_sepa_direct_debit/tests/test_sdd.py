# Copyright 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# Copyright 2018-2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from lxml import etree

from odoo import fields
from odoo.exceptions import UserError
from odoo.tools import file_open, float_compare

from .common import AccountBankingSepaDirectDebitCommon


class TestSDD(AccountBankingSepaDirectDebitCommon):
    def test_01_pain_008_001_02_core(self):
        self.check_sdd("pain.008.001.02", "FR78ZZZ424242")

    def test_02_pain_008_003_02_b2b_and_mode_identifier(self):
        self.mandate2.scheme = "B2B"
        self.payment_mode.sepa_creditor_identifier = "FR72ZZZ123456"
        self.check_sdd("pain.008.003.02", "FR72ZZZ123456")

    def test_03_pain_008_001_03(self):
        self.check_sdd("pain.008.001.03", "FR78ZZZ424242")

    def test_04_pain_008_001_04(self):
        self.check_sdd("pain.008.001.04", "FR78ZZZ424242")

    def test_05_grouping_by_requested_date(self):
        self.mandate12.type = "recurrent"
        self.mandate12.recurrent_sequence_type = "first"
        self.check_sdd(
            "pain.008.001.02",
            "FR78ZZZ424242",
            oneoff=False,
            different_dates=True,
        )

    def test_06_final_recurrent_sequence_expires(self):
        self.mandate2.recurrent_sequence_type = "final"
        self.check_sdd("pain.008.001.02", "FR78ZZZ424242", sequence_type="final")

    def test_07_recurring_sequence_stays_valid(self):
        self.mandate2.recurrent_sequence_type = "recurring"
        self.check_sdd("pain.008.001.02", "FR78ZZZ424242", sequence_type="recurring")

    def test_08_missing_mandate_is_rejected(self):
        self.payment_mode.payment_method_id.mandate_required = True
        partner = self.env["res.partner"].create(
            {
                "name": "Customer without a mandate",
                "company_id": self.company.id,
                "property_account_payable_id": self.account_payable_company_B.id,
                "property_account_receivable_id": self.account_receivable_company_B.id,
            }
        )
        invoice = self.create_invoice(partner.id, False, 42.0)
        self.assertFalse(invoice.mandate_id)
        action = invoice.create_account_payment_line()
        payment_order = self.payment_order_model.browse(action["res_id"])
        with self.assertRaisesRegex(UserError, "Missing Mandate"):
            payment_order.draft2open()

    def test_09_cancelled_mandate_is_not_selected(self):
        self.payment_mode.payment_method_id.mandate_required = True
        self.mandate2.cancel()
        invoice = self.create_invoice(self.partner_agrolait.id, False, 42.0)
        self.assertFalse(invoice.mandate_id)
        action = invoice.create_account_payment_line()
        payment_order = self.payment_order_model.browse(action["res_id"])
        with self.assertRaisesRegex(UserError, "Missing Mandate"):
            payment_order.draft2open()

    def check_sdd(
        self,
        pain_version,
        expected_creditor_identifier,
        oneoff=True,
        different_dates=False,
        sequence_type="first",
    ):
        self.payment_mode.payment_method_id.write(
            {"pain_version": pain_version, "mandate_required": True}
        )
        self.mandate2.recurrent_sequence_type = sequence_type
        invoice1 = self.create_invoice(self.partner_agrolait.id, self.mandate2, 42.0)
        if oneoff:
            self.mandate12.type = "oneoff"
        invoice2 = self.create_invoice(self.partner_c2c.id, self.mandate12, 11.0)
        action = False
        for invoice in (invoice1, invoice2):
            action = invoice.create_account_payment_line()
        self.assertEqual(action["res_model"], "account.payment.order")
        payment_order = self.payment_order_model.browse(action["res_id"])
        self.assertEqual(payment_order.payment_type, "inbound")
        self.assertEqual(payment_order.payment_mode_id, self.payment_mode)
        self.assertEqual(payment_order.journal_id, self.bank_journal)

        agrolait_pay_line = payment_order.payment_line_ids.filtered(
            lambda line: line.partner_id == self.partner_agrolait
        )
        self.assertEqual(len(agrolait_pay_line), 1)
        self.assertEqual(agrolait_pay_line.currency_id, self.eur_currency)
        self.assertEqual(agrolait_pay_line.mandate_id, invoice1.mandate_id)
        self.assertEqual(
            agrolait_pay_line.partner_bank_id, invoice1.mandate_id.partner_bank_id
        )
        precision = self.env["decimal.precision"].precision_get("Account")
        self.assertEqual(
            float_compare(
                agrolait_pay_line.amount_currency, 42, precision_digits=precision
            ),
            0,
        )
        self.assertEqual(agrolait_pay_line.communication_type, "normal")
        self.assertEqual(agrolait_pay_line.communication, invoice1.name)

        payment_order._compute_sepa()
        payment_order.draft2open()
        self.assertEqual(payment_order.state, "open")
        self.assertTrue(payment_order.sepa)
        payments = payment_order.payment_ids
        self.assertEqual(len(payments), 2)
        self.assertEqual(
            float_compare(
                sum(payments.mapped("amount")), 53.0, precision_digits=precision
            ),
            0,
        )
        if different_dates:
            payments[1].payment_line_ids[:1].date = payments[0].payment_line_ids[
                :1
            ].date + timedelta(days=1)
        action = payment_order.open2generated()
        self.assertEqual(payment_order.state, "generated")
        self.assertEqual(action["res_model"], "ir.attachment")
        attachment = self.attachment_model.browse(action["res_id"])
        self.assertTrue(attachment.name.endswith(".xml"))
        xml_file = bytes(attachment.raw)
        xml_root = etree.fromstring(xml_file)
        namespaces = {"p": xml_root.nsmap[None]}
        xsd_path = f"account_banking_sepa_direct_debit/data/{pain_version}.xsd"
        with file_open(xsd_path) as xsd_file:
            schema = etree.XMLSchema(etree.parse(xsd_file))
        schema.assertValid(xml_root)

        payment_infos = xml_root.xpath("//p:PmtInf", namespaces=namespaces)
        self.assertEqual(len(payment_infos), 2)
        self.assertEqual(
            xml_root.xpath("string(//p:GrpHdr/p:NbOfTxs)", namespaces=namespaces), "2"
        )
        self.assertEqual(
            xml_root.xpath("string(//p:GrpHdr/p:CtrlSum)", namespaces=namespaces),
            "53.00",
        )
        self.assertEqual(
            [
                int(value)
                for value in xml_root.xpath(
                    "//p:PmtInf/p:NbOfTxs/text()", namespaces=namespaces
                )
            ],
            [1, 1],
        )
        self.assertCountEqual(
            xml_root.xpath(
                "//p:PmtInf/p:PmtTpInf/p:LclInstrm/p:Cd/text()", namespaces=namespaces
            ),
            [self.mandate2.scheme, self.mandate12.scheme],
        )
        self.assertCountEqual(
            xml_root.xpath(
                "//p:PmtInf/p:PmtTpInf/p:SeqTp/text()", namespaces=namespaces
            ),
            [
                {"first": "FRST", "recurring": "RCUR", "final": "FNAL"}[sequence_type],
                "OOFF" if oneoff else "FRST",
            ],
        )
        self.assertCountEqual(
            xml_root.xpath("//p:PmtInf/p:CtrlSum/text()", namespaces=namespaces),
            ["42.00", "11.00"],
        )
        instruction_ids = xml_root.xpath(
            "//p:DrctDbtTxInf/p:PmtId/p:EndToEndId/text()", namespaces=namespaces
        )
        self.assertEqual(len(instruction_ids), 2)
        self.assertEqual(len(set(instruction_ids)), 2)

        creditor_identifiers = xml_root.xpath(
            "//p:CdtrSchmeId//p:Id/text()", namespaces=namespaces
        )
        self.assertIn(expected_creditor_identifier, creditor_identifiers)
        creditor_accounts = xml_root.xpath(
            "//p:PmtInf/p:CdtrAcct/p:Id/p:IBAN/text()", namespaces=namespaces
        )
        self.assertTrue(creditor_accounts)
        self.assertTrue(
            all(
                account == self.company_bank.account_number.replace(" ", "")
                for account in creditor_accounts
            )
        )
        requested_dates = {
            fields.Date.to_string(date) for date in payments.mapped("payment_line_date")
        }
        xml_requested_dates = set(
            xml_root.xpath("//p:PmtInf/p:ReqdColltnDt/text()", namespaces=namespaces)
        )
        self.assertEqual(xml_requested_dates, requested_dates)
        if different_dates:
            self.assertEqual(len(xml_requested_dates), 2)

        # Generating the file alone must not consume a mandate or change its sequence.
        self.assertEqual(self.mandate2.state, "valid")
        self.assertEqual(self.mandate2.recurrent_sequence_type, sequence_type)
        self.assertFalse(self.mandate2.last_debit_date)
        self.assertEqual(self.mandate12.state, "valid")
        self.assertFalse(self.mandate12.last_debit_date)
        payment_order.generated2uploaded()
        self.assertEqual(payment_order.state, "uploaded")
        self.assertTrue(self.mandate2.last_debit_date)
        if sequence_type == "first":
            self.assertEqual(self.mandate2.recurrent_sequence_type, "recurring")
        elif sequence_type == "final":
            self.assertEqual(self.mandate2.state, "expired")
        else:
            self.assertEqual(self.mandate2.recurrent_sequence_type, "recurring")
        if oneoff:
            self.assertEqual(self.mandate12.state, "expired")
            self.assertFalse(self.partner_c2c.valid_mandate_id)
        else:
            self.assertEqual(self.mandate12.recurrent_sequence_type, "recurring")

    def create_invoice(self, partner_id, mandate, price_unit, inv_type="out_invoice"):
        invoice_lines = [
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
                "currency_id": self.eur_currency.id,
                "move_type": inv_type,
                "journal_id": self.journal_sale_company_B.id,
                "date": fields.Date.today(),
                "payment_mode_id": self.payment_mode.id,
                "mandate_id": mandate.id if mandate else False,
                "invoice_line_ids": invoice_lines,
            }
        )
        invoice.action_post()
        return invoice
