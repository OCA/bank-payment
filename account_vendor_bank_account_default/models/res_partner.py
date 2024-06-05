# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    default_bank_id = fields.Many2one(
        string="Default Bank Account",
        comodel_name="res.partner.bank",
        domain="[('partner_id', '=', commercial_partner_id)]",
        compute="_compute_default_bank_id",
        inverse="_inverse_default_bank_id",
        store=True,
        readonly=False,
    )
    user_default_bank_id = fields.Many2one(
        comodel_name="res.partner.bank",
        string="User Default Bank Account",
    )
    has_default_bank_id = fields.Boolean(
        string="Has Default Bank Account",
        default=True,
    )

    @api.depends("bank_ids", "user_default_bank_id")
    def _compute_default_bank_id(self):
        for rec in self:
            rec.default_bank_id = rec.user_default_bank_id or rec.bank_ids[:1]

    def _inverse_default_bank_id(self):
        for rec in self:
            rec.user_default_bank_id = rec.default_bank_id
            if not rec.user_default_bank_id:
                rec._compute_default_bank_id()

    @api.model
    def _commercial_fields(self):
        res = super()._commercial_fields()
        res += ["default_bank_id", "user_default_bank_id", "has_default_bank_id"]
        return res
