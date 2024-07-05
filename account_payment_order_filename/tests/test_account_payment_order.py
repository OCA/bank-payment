# Copyright 2024 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from contextlib import contextmanager

from lxml import etree

from odoo.tests.common import TransactionCase


class TestAccountPaymentOrder(TransactionCase):
    """
    Tests for account.payment.order
    """

    @contextmanager
    def _skip_validate_xml(self):
        def _validate_xml(this_self, xml_string, gen_args):
            return True

        self.PaymentOrder._patch_method("_validate_xml", _validate_xml)
        yield
        self.PaymentOrder._revert_method("_validate_xml")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.PaymentMode = cls.env["account.payment.mode"]
        cls.PaymentOrder = cls.env["account.payment.order"]
        cls.Sequence = cls.env["ir.sequence"]
        cls.sequence = cls.Sequence.create(
            {
                "name": "Test sequence pay",
                "code": "test.custom.sequence",
                "prefix": "",
                "suffix": ".xml",
                "padding": 2,
                "number_next": 1,
                "number_increment": 1,
                "company_id": False,
            }
        )
        cls.creation_mode = cls.PaymentMode.create(
            {
                "name": "Test Direct Debit of suppliers from Société Générale",
                "company_id": cls.env.company.id,
                "bank_account_link": "variable",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
                "filename_sequence_id": cls.sequence.id,
            }
        )
        cls.payment_order = cls.PaymentOrder.create(
            {
                "payment_type": "outbound",
                "payment_mode_id": cls.creation_mode.id,
            }
        )
        cls.gen_args = {
            "pain_flavor": "",
            "file_prefix": "",
        }
        nsmap = {
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
            None: "urn:iso:std:iso:20022:tech:xsd:%s" % "boh",
        }
        attrib = {}
        cls.xml_root = etree.Element("Document", nsmap=nsmap, attrib=attrib)

    def test_get_filename_with_sequence_filled(self):
        """
        Ensure the sequence is correctly used to generate the filename.
        """
        self.assertTrue(self.payment_order)
        with self._skip_validate_xml():
            _xml_content, filename = self.payment_order.finalize_sepa_file_creation(
                self.xml_root, self.gen_args.copy()
            )
        expected_filename = "01.xml"  # As it's the first time we generate it
        self.assertEqual(expected_filename, filename)

    def test_get_filename_with_sequence_not_filled(self):
        """
        Ensure the original filename is kept when the sequence is not set
        """
        self.assertTrue(self.payment_order)
        self.payment_order.payment_mode_id.write({"filename_sequence_id": False})
        expected_filename = "{}{}.xml".format(
            self.gen_args["file_prefix"], self.payment_order.name
        )
        with self._skip_validate_xml():
            _xml_content, filename = self.payment_order.finalize_sepa_file_creation(
                self.xml_root, self.gen_args.copy()
            )
        self.assertEqual(expected_filename, filename)
