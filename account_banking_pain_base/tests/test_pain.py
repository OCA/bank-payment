# Copyright 2024 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from lxml import etree

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestAccountBankingPainBase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.demo_partner = cls.env.ref("base.partner_demo")
        cls.eur = cls.env.ref("base.EUR")
        cls.tnd = cls.env.ref("base.TND")
        cls.jpy = cls.env.ref("base.JPY")
        cls.pay_obj = cls.env["account.payment.order"]

    def test_prepare_field(self):
        gen_args = {"convert_to_ascii": True}
        allowed_chars = "abcABC0123456789/-?:().,' "
        self.assertEqual(
            self.pay_obj._prepare_field(
                "TEST", "allowed_chars", {"allowed_chars": allowed_chars}, 140, gen_args
            ),
            allowed_chars,
        )
        testmap = {
            '42üûéèàÉÈ?@"^': "42uueeaEE?---",
            "({non %*€})": "(-non --EUR-)",
            "_Niña$;,[]": "-Nina--,--",
            "ça va /pas!.\\|": "ca va /pas-.--",
            "narrow white space:\u2009.": "narrow white space: .",
        }
        for src, dest in testmap.items():
            self.assertEqual(
                self.pay_obj._prepare_field("TEST", "src", {"src": src}, 140, gen_args),
                dest,
            )
        boolean_value = False
        with self.assertRaises(UserError):
            self.pay_obj._prepare_field(
                "TEST", "boolean_value", {"boolean_value": boolean_value}, 140, gen_args
            )
        integer_value = 42
        with self.assertRaises(UserError):
            self.pay_obj._prepare_field(
                "TEST", "integer_value", {"integer_value": integer_value}, 140, gen_args
            )
        float_value = 42.12
        with self.assertRaises(UserError):
            self.pay_obj._prepare_field(
                "TEST", "float_value", {"float_value": float_value}, 140, gen_args
            )
        string_with_typo = "123@ûZZZ"
        self.assertEqual(
            self.pay_obj._prepare_field(
                "TEST",
                "string_with_typo",
                {"string_with_typo": string_with_typo},
                5,
                gen_args,
            ),
            "123-u",
        )

    def test_split_street_into_name_number(self):
        street2res = {
            " 7 rue Henri Rolland ": ("rue Henri Rolland", "7"),
            "27, rue Henri Rolland": ("rue Henri Rolland", "27"),
            "27,rue Henri Rolland": ("rue Henri Rolland", "27"),
            "55A rue du Tonkin": ("rue du Tonkin", "55A"),
            "55 A rue du Tonkin": ("rue du Tonkin", "55 A"),
            "55.A rue du Tonkin": ("rue du Tonkin", "55 A"),
            "35bis, rue Montgolfier": ("rue Montgolfier", "35bis"),
            "35 bis, rue Montgolfier": ("rue Montgolfier", "35 bis"),
            "35BIS, rue Montgolfier": ("rue Montgolfier", "35BIS"),
            "35 BIS rue Montgolfier": ("rue Montgolfier", "35 BIS"),
            "27ter, rue René Coty": ("rue René Coty", "27ter"),
            "27 Quarter rue René Coty": ("rue René Coty", "27 Quarter"),
            "1242 chemin des Bauges": ("chemin des Bauges", "1242"),
            "12242 RD 123": ("RD 123", "12242"),
            "122 rue du Général de division Tartempion": (
                "rue du Général de division Tartempion",
                "122",
            ),
            "Kirchenstrasse 177": ("Kirchenstrasse", "177"),
            "Place des Carmélites": ("Place des Carmélites", False),
            "123 Bismark avenue": ("Bismark avenue", "123"),
            "34 av Barthelemy Buyer": ("av Barthelemy Buyer", "34"),
            "4 bd des Belges": ("bd des Belges", "4"),
            "  ": (False, False),
        }
        for street, (exp_street_name, exp_street_number) in street2res.items():
            street_name, street_number = self.env[
                "res.partner"
            ]._split_street_into_name_number(street)
            self.assertEqual(street_name, exp_street_name)
            self.assertEqual(street_number, exp_street_number)

    def test_generate_sepa_pain_address_block(self):
        root = etree.Element("root")
        self.demo_partner._generate_sepa_pain_address_block(
            root,
            {
                "pain_flavor": "pain.001.001.03",
                "convert_to_ascii": True,
            },
        )
        root.xpath(".//StrtNm")
        self.assertEqual(root.xpath(".//StrtNm")[0].text, "Buena Vista Avenue")
        self.assertEqual(root.xpath(".//BldgNb")[0].text, "3575")
        self.assertEqual(root.xpath(".//PstCd")[0].text, "97401")
        self.assertEqual(root.xpath(".//TwnNm")[0].text, "Eugene")
        self.assertEqual(root.xpath(".//CtrySubDvsn")[0].text, "Cordoba")
        self.assertEqual(root.xpath(".//Ctry")[0].text, "US")

    def test_generate_sepa_pain_unstructured_address_block(self):
        root = etree.Element("root")
        self.demo_partner._generate_sepa_pain_address_block(
            root,
            {
                "pain_flavor": "pain.001.003.03",
                "convert_to_ascii": True,
            },
        )
        self.assertEqual(root.xpath(".//AdrLine")[0].text, "3575  Buena Vista Avenue")
        self.assertEqual(root.xpath(".//AdrLine")[1].text, "97401 Eugene")
        self.assertEqual(root.xpath(".//Ctry")[0].text, "US")
