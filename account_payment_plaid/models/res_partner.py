from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    plaid_client_id = fields.Char(string="client ID", unique=True)
