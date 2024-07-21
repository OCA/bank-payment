from odoo import _, api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    plaid_client_id = fields.Char(string="Client ID")
    plaid_secret = fields.Char(string="Secret")
    plaid_host = fields.Selection(
        string="Host",
        selection=[
            ("sand", _("Sandbox")),
            ("prod", _("Production")),
        ],
    )
    plaid_access_token = fields.Char(string="Access Token")

    plaid_account_id = fields.Many2one(
        string="Account ID", comodel_name="plaid.account", ondelete="set null"
    )

    @api.model
    def save_access_token(self, public_token, company_id):
        company_id = self.env["res.company"].browse(company_id)
        plaid_interface = self.env["plaid.interface"]
        client = plaid_interface._client(
            company_id.plaid_client_id, company_id.plaid_secret, company_id.plaid_host
        )
        company_id.plaid_access_token = plaid_interface._login(client, public_token)
        company_id._generate_plaid_accounts()

    def _prepare_account_vals(self, vals):
        currency_id = self.env["res.currency"].search(
            [("name", "=", vals["balances"]["iso_currency_code"])]
        )

        return {
            "name": vals["name"],
            "account": vals["account_id"],
            "currency_id": currency_id.id if currency_id else False,
            "official_name": vals["official_name"],
            "type": vals["type"],
            "mask": vals["mask"],
            "subtype": vals["subtype"],
        }

    def _create_plaid_accounts(self, accounts):
        PlaidAccount = self.env["plaid.account"]
        PlaidAccount.search([]).unlink()
        for account in accounts:
            PlaidAccount.create(self._prepare_account_vals(account))

    def _generate_plaid_accounts(self):
        plaid_interface = self.env["plaid.interface"]
        client = plaid_interface._client(
            self.plaid_client_id,
            self.plaid_secret,
            self.plaid_host,
        )
        accounts = plaid_interface._get_accounts(client, self.plaid_access_token)
        self._create_plaid_accounts(accounts)
