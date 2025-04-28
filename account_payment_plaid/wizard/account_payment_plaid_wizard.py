from odoo import _, fields, models
from odoo.exceptions import ValidationError


class AccountPaymentPlaidWizard(models.TransientModel):
    _name = "account.payment.plaid.wizard"

    partner_id = fields.Many2one("res.partner", string="Vendor")
    account_move_id = fields.Many2one("account.move", string="Account Move")
    amount = fields.Monetary()
    currency_id = fields.Many2one("res.currency", string="Currency")
    description = fields.Char()
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
                _("%(code)s: %(description)s")
                % {
                    "code": decision["decision_rationale"]["code"],
                    "description": decision["decision_rationale"]["description"],
                }
            )
        return decision["id"]

    def action_confirm(self):
        PlaidInterface = self.env["plaid.interface"]

        client = PlaidInterface._client(
            self.env.user.company_id.plaid_client_id,
            self.env.user.company_id.plaid_secret,
            self.env.user.company_id.plaid_host,
        )

        partner_bank = self.partner_id.bank_ids.filtered(
            lambda b: b.plaid_account_id and b.plaid_access_token
        )[:1]
        if not partner_bank:
            raise ValidationError(_("The vendor has no Plaid-connected bank account."))

        auth_data = PlaidInterface.transfer_auth_credit(
            client=client,
            access_token=partner_bank.plaid_access_token,
            account_id=partner_bank.plaid_account_id,
            amount=f"{self.amount:.2f}",
            receiver_name=self.partner_id.name,
            receiver_email=self.partner_id.email,
        )
        auth_id = self._verify_plaid_auth(auth_data)

        transfer = PlaidInterface.transfer_create_credit(
            client=client,
            access_token=partner_bank.plaid_access_token,
            account_id=partner_bank.plaid_account_id,
            authorization_id=auth_id,
            description=self.description[-14:],
        )

        self._create_transfer(transfer)
