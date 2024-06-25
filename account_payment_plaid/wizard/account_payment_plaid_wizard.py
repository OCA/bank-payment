from odoo import _, fields, models
from odoo.exceptions import ValidationError


class AccountPaymentPlaidWizard(models.TransientModel):
    _name = "account.payment.plaid.wizard"

    partner_id = fields.Many2one("res.partner", string="Vendor")
    account_move_id = fields.Many2one("account.move", string="Account Move")
    amount = fields.Monetary(string="Amount")
    currency_id = fields.Many2one("res.currency", string="Currency")
    description = fields.Char(string="Description")
    company_id = fields.Many2one("res.company", string="Company")

    def _create_transfer(self, transfer):
        res = self.env["plaid.transfer"].create(
            {
                "name": transfer["id"],
                "amount": self.amount,
                "state": transfer["status"],
                "currency_id": self.currency_id.id,
                "description": self.description,
                "account_move_id": self.account_move_id.id,
            }
        )
        return res

    def _verify_plaid_auth(self, decision):
        if decision["decision"] != "approved":
            raise ValidationError(
                _(
                    "%s: %s"
                    % (
                        decision["decision_rationale"]["code"],
                        decision["decision_rationale"]["description"],
                    )
                )
            )
        return decision["authorization_id"]

    def action_confirm(self):
        PlaidInterface = self.env["plaid.interface"]
        client_id = self.env.user.company_id.plaid_client_id
        secret = self.env.user.company_id.plaid_secret
        host = self.env.user.company_id.plaid_host
        client = PlaidInterface._client(client_id, secret, host)
        auth_id = self._verify_plaid_auth(
            PlaidInterface._transfer_auth(
                client=client,
                account_id=self.company_id.plaid_account_id.account,
                partner_id=self.partner_id,
                amount="{:.2f}".format(self.amount),
                access_token=self.company_id.plaid_access_token,
            )
        )
        self._create_transfer(
            PlaidInterface._transfer(
                client=client,
                access_token=self.company_id.plaid_access_token,
                account_id=self.company_id.plaid_account_id.account,
                authorization_id=auth_id,
                description=self.description[6:-1],
            )
        )
