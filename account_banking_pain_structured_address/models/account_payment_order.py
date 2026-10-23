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
            or not partner.city
            or not pain_flavor.startswith("pain.001.001.09")
            or self._get_pain09_address_mode(partner) != "structured"
        ):
            return super().generate_address_block(parent_node, partner, gen_args)
        postal_address = etree.SubElement(parent_node, "PstlAdr")
        # Same order as PostalAddress24 in the pain.001.001.09 schema
        for tag, field_name, value, max_size in (
            ("StrtNm", "partner.street_name", partner.street_name, 70),
            ("BldgNb", "partner.street_number", partner.street_number, 16),
            ("PstCd", "partner.zip", partner.zip, 16),
            ("TwnNm", "partner.city", partner.city, 35),
            ("Ctry", "partner.country_id.code", partner.country_id.code, 2),
        ):
            if not (value or "").strip():
                continue
            text = self._prepare_field(
                tag, field_name, {"partner": partner}, max_size, gen_args=gen_args
            ).strip()
            if text:
                etree.SubElement(postal_address, tag).text = text
        return True
