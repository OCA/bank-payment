# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_default_mandate_contact = fields.Selection(
        selection=[
            ("partner_id", "Customer Mandate"),
            ("commercial_partner_id", "Commercial Customer Mandate"),
            ("partner_invoice_id", "Invoice Address Mandate"),
            ("partner_shipping_id", "Delivery Address Mandate"),
        ],
        string="Default Sale Mandate Contact",
        help="The partner of the sales in which odoo will search for the mandate\n"
        "- Customer Mandate: Odoo will look the mandate in the sale partner,"
        " whether is an individual or the company\n"
        "- Commercial Customer Mandate: Odoo will look the mandate in the"
        " sale partner company\n"
        "- Invoice Address Mandate: Odoo will look the mandate in the"
        " sale invoice address\n"
        "- Delivery Address Mandate: Odoo will look the mandate in the"
        " sale delivery address\n"
        "- False: Odoo will use the company configuration option",
    )

    @api.model
    def _commercial_fields(self):
        return super()._commercial_fields() + [
            "sale_default_mandate_contact",
        ]
