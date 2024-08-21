# Copyright 2024 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestAccountBankingPainBase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.eur = cls.env.ref("base.EUR")
        cls.tnd = cls.env.ref("base.TND")
        cls.jpy = cls.env.ref("base.JPY")
        cls.pay_obj = cls.env["account.payment.order"]

    def test_currency_format_pain(self):
        # decimal places 2
        self.assertEqual(self.eur.decimal_places, 2)
        self.assertEqual(self.eur._pain_format(6.5500000000000001), "6.55")
        self.assertEqual(self.eur._pain_format(6.5), "6.50")
        self.assertEqual(self.eur._pain_format(6.9999999999999999), "7.00")
        self.assertEqual(self.eur._pain_format(23456.40000000000000000001), "23456.40")
        # decimal places = 3
        self.assertEqual(self.tnd.decimal_places, 3)
        self.assertEqual(self.tnd._pain_format(1234.45599999999999999999), "1234.456")
        self.assertEqual(self.tnd._pain_format(1234.4), "1234.400")
        self.assertEqual(self.tnd._pain_format(1234.00000000000000000001), "1234.000")
        # decimal places 0
        self.assertEqual(self.jpy.decimal_places, 0)
        self.assertEqual(self.jpy._pain_format(1234.99999999999999998), "1235")
        self.assertEqual(self.jpy._pain_format(112233.00000000000000000), "112233")

    def test_prepare_field(self):
        gen_args = {"convert_to_ascii": True}
        allowed_chars = "abcABC0123456789/-?:().,' "
        self.assertEqual(
            self.pay_obj._prepare_field("TEST", allowed_chars, 140, gen_args),
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
                self.pay_obj._prepare_field("TEST", src, 140, gen_args), dest
            )
        with self.assertRaises(UserError):
            self.pay_obj._prepare_field("TEST", False, 140, gen_args)
        with self.assertRaises(UserError):
            self.pay_obj._prepare_field("TEST", 42, 140, gen_args)
        with self.assertRaises(UserError):
            self.pay_obj._prepare_field("TEST", 42.12, 140, gen_args)
        self.assertEqual(
            self.pay_obj._prepare_field("TEST", "123@ûZZZ", 5, gen_args), "123-u"
        )
        with self.assertRaises(UserError):
            self.pay_obj._prepare_field(
                "TEST", "1234567", 5, gen_args, raise_if_oversized=True
            )
