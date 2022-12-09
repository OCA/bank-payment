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
        procesed_partners = self.browse()
        for partner in self:
            if partner.contact_mandate_id.state == "valid":
                partner.valid_mandate_id = partner.contact_mandate_id
                procesed_partners |= partner
        return super(ResPartner, self - procesed_partners)._compute_valid_mandate_id()
