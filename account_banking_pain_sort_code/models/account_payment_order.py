# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from lxml import etree
from odoo import api, models


class AccountPaymentOrder(models.Model):

    _inherit = 'account.payment.order'

    @api.model
    def generate_fininst_postal_address(self, parent_node, bank, gen_args):
        """
        Override this method as Bank Branch Code has to be inserted
        between BIC and Postal Address
        :param parent_node:
        :param bank:
        :param gen_args:
        :return:
        """
        sort_code = bank.sort_code
        if sort_code:
            party_agent_institution = parent_node
            if etree.iselement(party_agent_institution):
                clearing_system_member_id = etree.SubElement(
                    party_agent_institution, 'ClrSysMmbId')
                country = bank.country
                if country:
                    code = country.code.upper()
                    clearing_system_id = etree.SubElement(
                        clearing_system_member_id, 'ClrSysId')
                    proprietary = etree.SubElement(
                        clearing_system_id, 'Prtry')
                    proprietary.text = code
                member_id = etree.SubElement(
                    clearing_system_member_id, 'MmbId')
                member_id.text = sort_code
        super(AccountPaymentOrder, self).generate_fininst_postal_address(
            parent_node=parent_node,
            bank=bank,
            gen_args=gen_args)
        return
