# -*- coding: utf-8 -*-
# Copyright 2018 brain-tec AG (https://www.braintec-group.com/)
# @author: Timka Piric Muratovic, Tobias Bächle
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    @api.model
    def generate_party_agent(self, parent_node, party_type, order, partner_bank, gen_args, bank_line=None):
        """
        Identify and generate the party agent information based on the csmi_number if it is set for the bank.
        Otherwise resort to the default implementation.
        """
        if partner_bank.bank_id.csmi != 'other' and partner_bank.bank_id.csmi_number:
            party_agent = etree.SubElement(
                parent_node, '%sAgt' % party_type)
            party_agent_institution = etree.SubElement(
                party_agent, 'FinInstnId')
            party_agent_csmi = etree.SubElement(
                party_agent_institution, 'ClrSysMmbId')
            party_agent_csmi_identification = etree.SubElement(
                party_agent_csmi, 'ClrSysId')
            party_agent_csmi_identification_code = etree.SubElement(
                party_agent_csmi_identification, 'Cd')
            party_agent_csmi_identification_code.text = partner_bank.bank_id.csmi

            party_agent_csmi_identification_member_id = etree.SubElement(
                party_agent_csmi, 'MmbId')
            party_agent_csmi_identification_member_id.text = partner_bank.bank_id.csmi_number
            party_agent_name = etree.SubElement(
                party_agent_institution, 'Nm')
            party_agent_name.text = partner_bank.bank_id.name
            party_agent_postal_address = etree.SubElement(
                party_agent_institution, 'PstlAdr')
            if partner_bank.bank_id.street:
                party_agent_postal_street_name = etree.SubElement(
                    party_agent_postal_address, 'StrtNm')
                party_agent_postal_street_name.text = partner_bank.bank_id.street
            if partner_bank.bank_id.zip:
                party_agent_postal_street_zip = etree.SubElement(
                    party_agent_postal_address, 'PstCd')
                party_agent_postal_street_zip.text = partner_bank.bank_id.zip
            if partner_bank.bank_id.city:
                party_agent_postal_street_city = etree.SubElement(
                    party_agent_postal_address, 'TwnNm')
                party_agent_postal_street_city.text = partner_bank.bank_id.city
            if not partner_bank.bank_id.country:
                raise UserError(
                    _("Country of the bank '%s' is missing. This is needed for international payments.")
                    % (partner_bank.bank_id.name))
            else:
                party_agent_postal_street_country = etree.SubElement(
                    party_agent_postal_address, 'Ctry')
                party_agent_postal_street_country.text = partner_bank.bank_id.country.code

            return True
        else:
            return super(AccountPaymentOrder, self).generate_party_agent(parent_node, party_type, order, partner_bank,
                                                                         gen_args, bank_line=bank_line)
