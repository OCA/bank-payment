from odoo import fields, models


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    plaid_access_token = fields.Char()
    plaid_account_id = fields.Char()
    plaid_subtype = fields.Char()
    plaid_routing_number = fields.Char()
