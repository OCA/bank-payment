from odoo import fields, models


class PlaidAccount(models.Model):
    _name = "plaid.account"

    name = fields.Char(string="Name", required=True)
    account = fields.Char(string="Account ID", required=True)
    currency_id = fields.Many2one("res.currency", string="Currency")
    official_name = fields.Char(string="Official Name")
    type = fields.Char(string="Type")
    mask = fields.Char(string="Mask")
    subtype = fields.Char(string="Subtype")
    company_id = fields.Many2one(
        comodel_name="res.company", default=lambda self: self.env.company.id
    )
