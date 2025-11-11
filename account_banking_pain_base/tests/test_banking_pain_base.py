# Copyright 2025
# Copyright 2026 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from lxml import etree

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestBankingPainBase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Company = cls.env.company
        cls.Bank = cls.env["res.bank"].sudo()
        cls.ResPartnerBank = cls.env["res.partner.bank"].sudo()
        cls.Journal = cls.env["account.journal"].sudo()
        cls.PaymentMode = cls.env["account.payment.mode"].sudo()
        cls.PaymentOrder = cls.env["account.payment.order"].sudo()
        cls.bank = cls.Bank.create({"name": "The Bank"})
        cls.partner_bank = cls.ResPartnerBank.create(
            {
                "acc_number": "NL00TRIO0123456789",
                "partner_id": cls.Company.partner_id.id,
                "bank_id": cls.bank.id,
            }
        )
        cls.journal = cls.Journal.create(
            {
                "name": "Hybrid Test The Bank",
                "type": "bank",
                "code": "HBD",
                "bank_account_id": cls.partner_bank.id,
                "company_id": cls.Company.id,
            }
        )
        manual_out = cls.env.ref("account.account_payment_method_manual_out")
        cls.pay_mode = cls.PaymentMode.create(
            {
                "name": "Hybrid Mode",
                "company_id": cls.Company.id,
                "payment_method_id": manual_out.id,
                "payment_type": "outbound",
                "bank_account_link": "fixed",
                "fixed_journal_id": cls.journal.id,
            }
        )
        cls.payment_method = cls.pay_mode.payment_method_id
        cls.po = cls.PaymentOrder.create(
            {
                "name": "PO-HYB",
                "payment_mode_id": cls.pay_mode.id,
                "payment_type": "outbound",
                "journal_id": cls.journal.id,
            }
        )

    def test_hybrid_address_block_city_only(self):
        country = self.env["res.country"].search([("code", "=", "NL")], limit=1)
        partner = self.env["res.partner"].create(
            {
                "name": "Hybrid Partner",
                "street": "Somewhere",
                "zip": "5555 NN",
                "city": "Amersfoort",
                "country_id": country.id,
            }
        )
        gen_args = {"pain_flavor": "pain.001.001.03"}
        root = etree.Element("Root")
        self.po.with_context(export_bank_id=self.bank.id).generate_address_block(
            root, partner, gen_args
        )
        pstl_nodes = root.findall("PstlAdr")
        self.assertEqual(len(pstl_nodes), 1)
        pstl = pstl_nodes[0]
        ctry = pstl.find("Ctry")
        self.assertIsNotNone(ctry)
        self.assertEqual(ctry.text, partner.country_id.code)
        adr_lines = pstl.findall("AdrLine")
        self.assertGreaterEqual(len(adr_lines), 1)
        combined = " ".join([(line.text or "") for line in adr_lines])
        self.assertIn(partner.city, combined)
        self.assertIn(partner.zip, combined)
        self.assertIsNone(pstl.find("TwnNm"))

    def test_hybrid_address_block_pain09(self):
        country = self.env["res.country"].search([("code", "=", "NL")], limit=1)
        partner = self.env["res.partner"].create(
            {
                "name": "Hybrid Partner 09",
                "street": "Oudestraat 1",
                "street2": "2/2.14",
                "zip": "3942 NR",
                "city": "Adelala",
                "country_id": country.id,
            }
        )
        self.pay_mode.payment_method_id.sepa_pain09_address_mode = "minimal"
        gen_args = {"pain_flavor": "pain.001.001.09"}
        root = etree.Element("Root")
        self.po.generate_address_block(root, partner, gen_args)
        pstl = root.find("PstlAdr")
        self.assertIsNotNone(pstl)
        self.assertEqual(pstl.find("TwnNm").text, partner.city)
        self.assertEqual(pstl.find("Ctry").text, partner.country_id.code)
        # minimal
        self.assertIsNone(pstl.find("PstCd"))
        self.assertEqual(len(pstl.findall("AdrLine")), 0)

    def test_hybrid_address_block_pain09_requires_city(self):
        country = self.env["res.country"].search([("code", "=", "NL")], limit=1)
        partner = self.env["res.partner"].create(
            {
                "name": "Hybrid Partner 09 No City",
                "street": "Oudestraat 1",
                "zip": "3842 NK",
                "city": False,
                "country_id": country.id,
            }
        )
        gen_args = {"pain_flavor": "pain.001.001.09"}
        root = etree.Element("Root")
        with self.assertRaises(UserError):
            self.po.with_context(export_bank_id=self.bank.id).generate_address_block(
                root, partner, gen_args
            )

    def test_hybrid_address_block_pain09_hybrid(self):
        country = self.env["res.country"].search([("code", "=", "NL")], limit=1)
        partner = self.env["res.partner"].create(
            {
                "name": "Hybrid Partner 09 Hybrid",
                "street": "Oudestraat 1",
                "street2": "2/2.14",
                "zip": "3942 NR",
                "city": "Adelala",
                "country_id": country.id,
            }
        )
        self.pay_mode.payment_method_id.sepa_pain09_address_mode = "hybrid"
        gen_args = {"pain_flavor": "pain.001.001.09"}
        root = etree.Element("Root")
        self.po.with_context(export_bank_id=self.bank.id).generate_address_block(
            root, partner, gen_args
        )
        pstl = root.find("PstlAdr")
        self.assertIsNotNone(pstl)
        tags = [c.tag for c in list(pstl)]
        self.assertEqual(tags[0], "PstCd")
        self.assertEqual(tags[1], "TwnNm")
        self.assertEqual(tags[2], "Ctry")
        self.assertEqual(pstl.find("PstCd").text, partner.zip)
        self.assertEqual(pstl.find("TwnNm").text, partner.city)
        self.assertEqual(pstl.find("Ctry").text, partner.country_id.code)
        adr_lines = pstl.findall("AdrLine")
        self.assertEqual(len(adr_lines), 2)
        self.assertEqual(adr_lines[0].text, partner.street)
        self.assertEqual(adr_lines[1].text, partner.street2)

    def test_hybrid_mode_non_09(self):
        country = self.env["res.country"].search([("code", "=", "NL")], limit=1)
        partner = self.env["res.partner"].create(
            {"name": "Hybrid Non09", "city": "Amersfoort", "country_id": country.id}
        )
        gen_args = {"pain_flavor": "pain.001.001.03"}
        root = etree.Element("Root")
        self.po.with_context(export_bank_id=self.bank.id).generate_address_block(
            root, partner, gen_args
        )
        pstl = root.find("PstlAdr")
        self.assertIsNotNone(pstl)
        self.assertIsNone(pstl.find("TwnNm"))

    def test_requested_date_pain09(self):
        root = etree.Element("Root")
        gen_args = {
            "pain_flavor": "pain.001.001.09",
            "payment_method": "TRF",
        }
        requested_date = fields.Date.to_string(fields.Date.today())
        (
            payment_info,
            nb_of_transactions,
            control_sum,
        ) = self.po.generate_start_payment_info_block(
            parent_node=root,
            payment_info_ident="'TEST'",
            priority=False,
            local_instrument=False,
            category_purpose=False,
            sequence_type=False,
            requested_date=requested_date,
            eval_ctx={},
            gen_args=gen_args,
        )
        req = payment_info.find("ReqdExctnDt")
        self.assertIsNotNone(req)
        if req.text:
            self.assertEqual(req.text, requested_date)
        else:
            dt = req.find("Dt")
            self.assertIsNotNone(dt)
            self.assertEqual(dt.text, requested_date)
