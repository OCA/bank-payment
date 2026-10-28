# Copyright 2026 Vignesh Babu S
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from lxml import etree

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStructuredAddress(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        company = cls.env.company
        bank = cls.env["res.bank"].create({"name": "Structured Test Bank"})
        partner_bank = cls.env["res.partner.bank"].create(
            {
                "acc_number": "NL91ABNA0417164300",
                "partner_id": company.partner_id.id,
                "bank_id": bank.id,
            }
        )
        journal = cls.env["account.journal"].create(
            {
                "name": "Structured Test Bank",
                "type": "bank",
                "code": "STRB",
                "bank_account_id": partner_bank.id,
                "company_id": company.id,
            }
        )
        cls.pay_mode = cls.env["account.payment.mode"].create(
            {
                "name": "Structured Mode",
                "company_id": company.id,
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
                "payment_type": "outbound",
                "bank_account_link": "fixed",
                "fixed_journal_id": journal.id,
            }
        )
        cls.pay_mode.payment_method_id.sepa_pain09_address_mode = "structured"
        cls.order = cls.env["account.payment.order"].create(
            {
                "name": "PO-STRUCT",
                "payment_mode_id": cls.pay_mode.id,
                "payment_type": "outbound",
                "journal_id": journal.id,
            }
        )
        cls.country = cls.env.ref("base.nl")

    def _partner(self, **vals):
        return self.env["res.partner"].create(
            {
                "name": "Structured Partner",
                "zip": "3942 NR",
                "city": "Adelala",
                "country_id": self.country.id,
                **vals,
            }
        )

    def _address(self, partner, pain_flavor="pain.001.001.09", **gen_args):
        root = etree.Element("Root")
        self.order.generate_address_block(
            root, partner, {"pain_flavor": pain_flavor, **gen_args}
        )
        return root.find("PstlAdr")

    def _tags(self, address):
        return [node.tag for node in address]

    def test_structured_address(self):
        address = self._address(self._partner(street="Oudestraat 12"))
        self.assertEqual(
            self._tags(address), ["StrtNm", "BldgNb", "PstCd", "TwnNm", "Ctry"]
        )
        self.assertEqual(address.find("StrtNm").text, "Oudestraat")
        self.assertEqual(address.find("BldgNb").text, "12")
        self.assertEqual(address.find("PstCd").text, "3942 NR")
        self.assertEqual(address.find("TwnNm").text, "Adelala")
        self.assertEqual(address.find("Ctry").text, "NL")

    def test_structured_address_without_number(self):
        address = self._address(self._partner(street="Domplein"))
        self.assertEqual(self._tags(address), ["StrtNm", "PstCd", "TwnNm", "Ctry"])

    def test_structured_address_values_cut_to_schema_size(self):
        partner = self._partner(
            street_name="A" * 80,
            street_number="1" * 20,
            street_number2="B" * 80,
            street2="C" * 80,
        )
        address = self._address(partner)
        self.assertEqual(len(address.find("StrtNm").text), 70)
        self.assertEqual(len(address.find("BldgNb").text), 16)
        self.assertEqual(len(address.find("Room").text), 70)
        self.assertEqual(len(address.find("AdrLine").text), 70)

    def test_door_number_written_as_room(self):
        partner = self._partner(
            street_name="Oudestraat", street_number="12", street_number2="4B"
        )
        address = self._address(partner)
        self.assertEqual(
            self._tags(address),
            ["StrtNm", "BldgNb", "Room", "PstCd", "TwnNm", "Ctry"],
        )
        self.assertEqual(address.find("Room").text, "4B")

    def test_street2_written_as_address_line(self):
        partner = self._partner(street="Oudestraat 12", street2="c/o Finance")
        address = self._address(partner)
        self.assertEqual(
            self._tags(address),
            ["StrtNm", "BldgNb", "PstCd", "TwnNm", "Ctry", "AdrLine"],
        )
        self.assertEqual(address.find("AdrLine").text, "c/o Finance")

    def test_door_number_and_street2_together(self):
        partner = self._partner(
            street_name="Hauptstrasse",
            street_number="12",
            street_number2="Top 5",
            street2="Stiege 2",
        )
        address = self._address(partner)
        self.assertEqual(
            self._tags(address),
            ["StrtNm", "BldgNb", "Room", "PstCd", "TwnNm", "Ctry", "AdrLine"],
        )
        self.assertEqual(len(address.findall("AdrLine")), 1)

    def test_blank_door_number_and_street2_not_written(self):
        partner = self._partner(
            street_name="Oudestraat",
            street_number="12",
            street_number2="   ",
            street2="   ",
        )
        address = self._address(partner)
        self.assertEqual(
            self._tags(address), ["StrtNm", "BldgNb", "PstCd", "TwnNm", "Ctry"]
        )

    def test_uninstall_falls_back_to_hybrid(self):
        method = self.pay_mode.payment_method_id
        field = method._fields["sepa_pain09_address_mode"]
        field.ondelete["structured"](method)
        self.assertEqual(method.sepa_pain09_address_mode, "hybrid")

    def test_no_street_name_falls_back_to_hybrid(self):
        address = self._address(self._partner(street2="Building C"))
        self.assertEqual(self._tags(address), ["PstCd", "TwnNm", "Ctry", "AdrLine"])
        self.assertEqual(address.find("AdrLine").text, "Building C")

    def test_city_is_required(self):
        partner = self._partner(street="Oudestraat 12", city=False)
        with self.assertRaises(UserError):
            self._address(partner)

    def test_blank_city_is_required(self):
        partner = self._partner(street="Oudestraat 12", city="   ")
        with self.assertRaises(UserError):
            self._address(partner)

    def test_other_pain_versions_unchanged(self):
        address = self._address(
            self._partner(street="Oudestraat 12"), pain_flavor="pain.001.001.03"
        )
        self.assertIsNone(address.find("StrtNm"))
        self.assertIsNone(address.find("TwnNm"))
        self.assertTrue(address.findall("AdrLine"))

    def test_structured_address_without_postcode(self):
        address = self._address(self._partner(street="Oudestraat 12", zip=False))
        self.assertEqual(self._tags(address), ["StrtNm", "BldgNb", "TwnNm", "Ctry"])

    def test_structured_address_converted_to_ascii(self):
        partner = self._partner(
            street_name="Straße der Einheit",
            street_number="12#3",
            city="Zürich",
            country_id=self.env.ref("base.ch").id,
        )
        address = self._address(partner, convert_to_ascii=True)
        self.assertEqual(address.find("StrtNm").text, "Strasse der Einheit")
        self.assertEqual(address.find("BldgNb").text, "12-3")
        self.assertEqual(address.find("TwnNm").text, "Zurich")
        self.assertEqual(address.find("Ctry").text, "CH")

    def test_street_not_split_stays_in_street_name(self):
        address = self._address(self._partner(street="Rue de la Paix 3 bis"))
        self.assertEqual(self._tags(address), ["StrtNm", "PstCd", "TwnNm", "Ctry"])
        self.assertEqual(address.find("StrtNm").text, "Rue de la Paix 3 bis")

    def test_number_without_street_name_falls_back_to_hybrid(self):
        address = self._address(self._partner(street="12"))
        self.assertEqual(self._tags(address), ["PstCd", "TwnNm", "Ctry", "AdrLine"])
        self.assertEqual(address.find("AdrLine").text, "12")

    def test_blank_street_name_falls_back_to_hybrid(self):
        partner = self._partner(street="Oudestraat 5")
        partner.street_name = "   "
        address = self._address(partner)
        self.assertEqual(self._tags(address), ["PstCd", "TwnNm", "Ctry", "AdrLine"])
        self.assertIsNone(address.find("StrtNm"))

    def test_other_address_modes_unchanged(self):
        partner = self._partner(street="Oudestraat 12")
        self.pay_mode.payment_method_id.sepa_pain09_address_mode = "hybrid"
        self.assertEqual(
            self._tags(self._address(partner)), ["PstCd", "TwnNm", "Ctry", "AdrLine"]
        )
        self.pay_mode.payment_method_id.sepa_pain09_address_mode = "minimal"
        self.assertEqual(self._tags(self._address(partner)), ["TwnNm", "Ctry"])

    def test_creditor_party_block(self):
        creditor = self._partner(
            street="Straße der Einheit 12",
            zip="8001",
            city="Zürich",
            country_id=self.env.ref("base.ch").id,
        )
        bank = self.env["res.bank"].create(
            {"name": "Creditor Bank", "bic": "UBSWCHZH80A"}
        )
        creditor_bank = self.env["res.partner.bank"].create(
            {
                "acc_number": "CH9300762011623852957",
                "partner_id": creditor.id,
                "bank_id": bank.id,
            }
        )
        gen_args = {
            "pain_flavor": "pain.001.001.09",
            "bic_xml_tag": "BICFI",
            "name_maxsize": 140,
            "payment_method": "TRF",
            "convert_to_ascii": True,
        }
        root = etree.Element("CdtTrfTxInf")
        self.order.generate_party_block(root, "Cdtr", "C", creditor_bank, gen_args)
        self.assertEqual(self._tags(root), ["CdtrAgt", "Cdtr", "CdtrAcct"])
        self.assertEqual(self._tags(root.find("Cdtr")), ["Nm", "PstlAdr"])
        address = root.find("Cdtr/PstlAdr")
        self.assertEqual(
            self._tags(address), ["StrtNm", "BldgNb", "PstCd", "TwnNm", "Ctry"]
        )
        self.assertEqual(address.find("StrtNm").text, "Strasse der Einheit")
        self.assertEqual(address.find("BldgNb").text, "12")
        self.assertEqual(address.find("TwnNm").text, "Zurich")
        self.assertEqual(address.find("Ctry").text, "CH")
