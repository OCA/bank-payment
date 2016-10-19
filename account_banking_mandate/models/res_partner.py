# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    mandate_count = fields.Integer(
        compute='_compute_mandate_count', string="Number of Mandates",
        readonly=True)

    @api.multi
    def _compute_mandate_count(self):
        mandate_data = self.env['account.banking.mandate'].read_group(
            [('partner_id', 'in', self.ids)], ['partner_id'], ['partner_id'])
        mapped_data = dict([
            (mandate['partner_id'][0], mandate['partner_id_count'])
            for mandate in mandate_data])
        for partner in self:
            partner.mandate_count = mapped_data.get(partner.id, 0)
