# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    contact_mandate_id = fields.Many2one(
        comodel_name="account.banking.mandate",
        string="Contact Mandate",
    )

    def _compute_valid_mandate_id(self):
        partners_to_process = self.filtered(
            lambda x: x.contact_mandate_id.state == "valid"
        )
        for partner in partners_to_process:
            partner.valid_mandate_id = partner.contact_mandate_id
        return super(ResPartner, self - partners_to_process)._compute_valid_mandate_id()
