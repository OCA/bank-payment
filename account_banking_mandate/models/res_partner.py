# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    mandate_count = fields.Integer(
        compute='_compute_mandate_count', string="Number of Mandates",
        readonly=True)
    valid_mandate_id = fields.Many2one(
        comodel_name='account.banking.mandate',
        compute='compute_valid_mandate_id',
        string='First Valid Mandate')

    @api.multi
    def _compute_mandate_count(self):
        mandate_data = self.env['account.banking.mandate'].read_group(
            [('partner_id', 'in', self.ids)], ['partner_id'], ['partner_id'])
        mapped_data = dict([
            (mandate['partner_id'][0], mandate['partner_id_count'])
            for mandate in mandate_data])
        for partner in self:
            partner.mandate_count = mapped_data.get(partner.id, 0)

    @api.multi
    def compute_valid_mandate_id(self):
        # Dict for reducing the duplicated searches on parent/child partners
        mandates_dic = {}
        for partner in self:
            commercial_partner_id = partner.commercial_partner_id.id
            if commercial_partner_id in mandates_dic:
                partner.valid_mandate_id = mandates_dic[commercial_partner_id]
            else:
                mandates = partner.commercial_partner_id.bank_ids.mapped(
                    'mandate_ids').filtered(lambda x: x.state == 'valid')
                first_valid_mandate_id = mandates[:1].id
                partner.valid_mandate_id = first_valid_mandate_id
                mandates_dic[commercial_partner_id] = first_valid_mandate_id
