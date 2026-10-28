# Copyright 2026 Vignesh Babu S
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from lxml import etree

from odoo import api, models


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    def _get_pain09_address_mode(self, partner):
        mode = super()._get_pain09_address_mode(partner)
        if mode == "structured" and not (partner.street_name or "").strip():
            return "hybrid"
        return mode

    @api.model
    def generate_address_block(self, parent_node, partner, gen_args):
        pain_flavor = (gen_args.get("pain_flavor") or "").strip()
        if (
            not partner.country_id
            # A missing or blank City raises in account_banking_pain_base
            or not (partner.city or "").strip()
            or not pain_flavor.startswith("pain.001.001.09")
            or self._get_pain09_address_mode(partner) != "structured"
        ):
            return super().generate_address_block(parent_node, partner, gen_args)
        postal_address = etree.SubElement(parent_node, "PstlAdr")
        # Same order as PostalAddress24 in the pain.001.001.09 schema. street2
        # has no structured element, so it is kept as one AdrLine (hybrid
        # address: TwnNm and Ctry in their own elements, at most 2 AdrLine).
        for tag, field_name, value, max_size in (
            ("StrtNm", "partner.street_name", partner.street_name, 70),
            ("BldgNb", "partner.street_number", partner.street_number, 16),
            ("Room", "partner.street_number2", partner.street_number2, 70),
            ("PstCd", "partner.zip", partner.zip, 16),
            ("TwnNm", "partner.city", partner.city, 35),
            ("Ctry", "partner.country_id.code", partner.country_id.code, 2),
            ("AdrLine", "partner.street2", partner.street2, 70),
        ):
            if not (value or "").strip():
                continue
            text = self._prepare_field(
                tag, field_name, {"partner": partner}, max_size, gen_args=gen_args
            ).strip()
            if text:
                etree.SubElement(postal_address, tag).text = text
        return True
