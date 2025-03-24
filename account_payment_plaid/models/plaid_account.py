from odoo import fields, models


class PlaidAccount(models.Model):
    _name = "plaid.account"

    name = fields.Char(required=True)
    account = fields.Char(string="Account ID", required=True)
    currency_id = fields.Many2one("res.currency", string="Currency")
    official_name = fields.Char()
    type = fields.Char()
    mask = fields.Char()
    subtype = fields.Char()
    company_id = fields.Many2one(
        comodel_name="res.company", default=lambda self: self.env.company.id
    )
