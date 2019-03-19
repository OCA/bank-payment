# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from lxml import etree
from odoo.fields import first
from odoo.tests import common


class TestPainSortCode(common.TransactionCase):

    def setUp(self):
        super(TestPainSortCode, self).setUp()
        bank_obj = self.env['res.bank']
        partner_bank_obj = self.env['res.partner.bank']
        self.payment_order_obj = self.env['account.payment.order']

        # Add Partner Bank Sort Code
        self.partner = self.env.ref('base.res_partner_4')

        vals = {
            'name': 'BANK TEST',
            'sort_code': '10-20-30',
            'bic': 'BABEBBBE',
            'country': self.env.ref('base.uk').id,
        }
        self.bank = bank_obj.create(vals)

        vals = {
            'acc_number': '1234567890',
            'bank_id': self.bank.id,
            'partner_id': self.partner.id,
        }
        partner_bank_obj.create(vals)

    def _create_etree(self):
        """
        Just create the XML part we are interested in
        :return:
        """
        self.root = etree.Element('ROOT')
        self.party_agent_institution = etree.SubElement(
            self.root, 'FinInstnId')

    def test_sort_code(self):
        self._create_etree()
        self.payment_order_obj.generate_fininst_postal_address(
            self.party_agent_institution,
            first(self.partner.bank_ids.filtered(
                lambda b: b.bank_id.sort_code == '10-20-30')).bank_id,
            {}
        )
        self.assertEquals(
            '10-20-30',
            self.party_agent_institution.xpath('./ClrSysMmbId/MmbId')[0].text
        )
        self.assertEquals(
            'GB',
            self.party_agent_institution.xpath(
                './ClrSysMmbId/ClrSysId/Prtry')[0].text
        )
