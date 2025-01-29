# Copyright 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    mandate_count = fields.Integer(
        compute="_compute_mandate_count", string="Number of Mandates", readonly=True
    )
    valid_mandate_id = fields.Many2one(
        comodel_name="account.banking.mandate",
        compute="_compute_valid_mandate_id",
        string="First Valid Mandate",
    )

    def _compute_mandate_count(self):
        mandate_data = self.env["account.banking.mandate"]._read_group(
            [("partner_id", "in", self.ids)],
            groupby=["partner_id"],
            aggregates=["__count"],
        )
        mapped_data = {
            partner.id: mandate_count for (partner, mandate_count) in mandate_data
        }
        for partner in self:
            partner.mandate_count = mapped_data.get(partner.id, 0)

    @api.depends_context("company")
    def _compute_valid_mandate_id(self):
        # Dict for reducing the duplicated searches on parent/child partners
        company_id = self.env.company.id
        mandates_dic = {}
        for partner in self:
            commercial_partner_id = partner.commercial_partner_id.id
            if commercial_partner_id in mandates_dic:
                partner.valid_mandate_id = mandates_dic[commercial_partner_id]
            else:
                mandates = partner.commercial_partner_id.bank_ids.mapped(
                    "mandate_ids"
                ).filtered(
                    lambda x: x.state == "valid" and x.company_id.id == company_id
                )
                first_valid_mandate_id = mandates[:1].id
                partner.valid_mandate_id = first_valid_mandate_id
                mandates_dic[commercial_partner_id] = first_valid_mandate_id
