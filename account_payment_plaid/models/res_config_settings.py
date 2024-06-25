from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
        readonly=True,
        ondelete="cascade",
    )

    plaid_client_id = fields.Char(
        readonly=False,
        related="company_id.plaid_client_id",
        string="Client ID",
        config_parameter="plaid_connector.plaid_client_id",
    )

    plaid_secret = fields.Char(
        string="Secret",
        readonly=False,
        related="company_id.plaid_secret",
        config_parameter="plaid_connector.plaid_secret",
    )
    plaid_host = fields.Selection(
        string="Host",
        readonly=False,
        default="sand",
        related="company_id.plaid_host",
        config_parameter="plaid_connector.plaid_host",
    )

    plaid_access_token = fields.Char(
        related="company_id.plaid_access_token", string="Access Token"
    )

    plaid_account_id = fields.Many2one(
        related="company_id.plaid_account_id",
        string="Account ID",
        readonly=False,
    )

    def action_sync_with_plaid(self):
        plaid_interface = self.env["plaid.interface"]
        client = plaid_interface._client(
            self.plaid_client_id, self.plaid_secret, self.plaid_host
        )
        lang = self.env["res.lang"].search([("code", "=", self.env.user.lang)]).iso_code
        company_name = self.env.user.company_id.name
        country_code = self.env.user.company_id.country_id.code
        link_token = plaid_interface._link(
            client=client,
            language=lang,
            country_code=country_code,
            company_name=company_name,
            products=["auth", "transfer"],
        )
        return {
            "type": "ir.actions.client",
            "tag": "plaid_login",
            "params": {
                "call_model": "res.company",
                "call_method": "save_access_token",
                "token": link_token,
                "object_id": self.env.user.company_id.id,
            },
            "target": "new",
        }
