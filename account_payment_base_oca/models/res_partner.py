# Copyright 2025 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # add selectable=True in domain
    property_outbound_payment_method_line_id = fields.Many2one(
        domain=lambda self: [
            ("payment_type", "=", "outbound"),
            ("company_id", "=", self.env.company.id),
            ("selectable", "=", True),
        ]
    )
    property_inbound_payment_method_line_id = fields.Many2one(
        domain=lambda self: [
            ("payment_type", "=", "inbound"),
            ("company_id", "=", self.env.company.id),
            ("selectable", "=", True),
        ]
    )
