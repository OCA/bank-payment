# Copyright 2024 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
import re

from lxml import objectify

from odoo import api, models

logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _generate_address_block(self, parent_node, gen_args):
        """Generate the piece of the XML corresponding to address block
        Following EPC guidelines:
        https://www.europeanpaymentscouncil.eu/document-library/guidance-documents/
        guidance-use-structured-addresses-2025-sepa-payment-schemes
        """
        self.ensure_one()
        if gen_args["pain_flavor"].startswith(("pain.001.003.03", "pain.008.003.02")):
            return self._generate_unstructured_address_block(parent_node, gen_args)
        apoo = self.env["account.payment.order"]
        if self.country_id:
            postal_address = objectify.SubElement(parent_node, "PstlAdr")
            street = self.street
            street2 = self.street2
            if street2 and not street:
                street = street2
                street2 = False
            if street2 and gen_args["pain_flavor"].startswith("pain.001.001.03"):
                postal_address.Dept = apoo._prepare_field(
                    "Department (Street 2)", street2, 70, gen_args
                )
            if street:
                # fields added by official module 'base_address_extended'
                if (
                    hasattr(self, "street_name")
                    and hasattr(self, "street_number")
                    and hasattr(self, "street_number2")
                ):
                    street_name = self.street_name
                    street_number = self.street_number
                    door = self.street_number2
                else:
                    # I don't use tools.street_split() because it doesn't work in many scenarios
                    # for example, in France, street are usually written as:
                    # 27, rue Henri Rolland
                    # but tools.street_split() only works when street number is written
                    # at the end, so I added a method _improved_street_split() below
                    street_name, street_number = self._improved_street_split(
                        self.street
                    )
                    door = False
                if street_name:
                    postal_address.StrtNm = apoo._prepare_field(
                        "Street Name", street_name, 70, gen_args
                    )
                if street_number:
                    postal_address.BldgNb = apoo._prepare_field(
                        "Street Number", street_number, 16, gen_args
                    )
                if door:
                    postal_address.Room = apoo._prepare_field(
                        "Door", door, 70, gen_args
                    )
            if self.zip:
                postal_address.PstCd = apoo._prepare_field(
                    "ZIP Code", self.zip, 16, gen_args
                )
            if self.city:
                postal_address.TwnNm = apoo._prepare_field(
                    "City", self.city, 35, gen_args
                )
            if street2 and gen_args["pain_flavor"].startswith("pain.001.001.09"):
                postal_address.TwnLctnNm = apoo._prepare_field(
                    "Town Location Name (Street 2)", street2, 35, gen_args
                )
            if self.state_id:
                # Better to write state name in the lang of the partner
                # for example: for a US partner, we should write its state name in English
                # and not in the user's lang
                postal_address.CtrySubDvsn = apoo._prepare_field(
                    "State",
                    self.with_context(
                        lang=self.lang or self.env.user.lang
                    ).state_id.name,
                    35,
                    gen_args,
                )

            postal_address.Ctry = self.country_id.code

    @api.model
    def _improved_street_split(self, street):
        # This method is fully tested in tests/test_pain.py
        logger.debug("_improved_street_split called on '%s'", street)
        street = street and street.strip()
        if not street:
            return (False, False)
        street = street.replace(",", " ")
        street = street.replace(".", " ")
        # replace all multi-spaces by one space
        street = " ".join(street.split())

        street_split = street.split(" ")
        # Handle '22 bis rue Henri Rolland' and 'Edmond street 48 B'
        if len(street_split) > 2:
            if street_split[
                0
            ].isdigit() and self._improved_street_split_street_number_ext(
                street_split[1]
            ):
                street_name = " ".join(street_split[2:])
                street_number = " ".join(street_split[:2])
                return (street_name, street_number)
            elif street_split[
                -2
            ].isdigit() and self._improved_street_split_street_number_ext(
                street_split[-1]
            ):
                street_name = " ".join(street_split[:-2])
                street_number = " ".join(street_split[-2:])
                return (street_name, street_number)

        # Search street number in first and last block: it just has to start by a digit
        if street_split[0][0].isdigit():
            street_number = street_split[0]
            street_name = " ".join(street_split[1:])
        elif street_split[-1][0].isdigit():
            street_number = street_split[-1]
            street_name = " ".join(street_split[:-1])
        else:
            street_number = False
            street_name = street
        return (street_name, street_number)

    @api.model
    def _improved_street_split_street_number_ext(self, text):
        # text is already stripped
        assert text
        if not re.match(r"[a-zA-Z]", text):
            return False
        if len(text) == 1:
            return True
        if text.lower() in ("bis", "ter", "quarter"):
            return True
        return False

    def _generate_unstructured_address_block(self, parent_node, gen_args):
        """Generation of unstructured address block is deprecated according to EPC
        and will not be allowed after nov 2025
        But the german variant pain.001.003.03 still requires it
        """
        apoo = self.env["account.payment.order"]
        if self.country_id:
            postal_address = objectify.SubElement(parent_node, "PstlAdr")
            postal_address.Ctry = self.country_id.code
            street_list = [self.street, self.street2]
            street = " - ".join([entry for entry in street_list if entry])
            if street:
                postal_address.AdrLine = apoo._prepare_field(
                    "Street as Address Line 1", street, 70, gen_args
                )
            zipcity_list = [self.zip, self.city]
            zipcity = " ".join([entry for entry in zipcity_list if entry])
            if zipcity:
                postal_address.AdrLine = apoo._prepare_field(
                    "Zip and City as Address Line 2", zipcity, 70, gen_args
                )
