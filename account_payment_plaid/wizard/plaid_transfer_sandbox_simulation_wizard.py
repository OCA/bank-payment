from odoo import _, fields, models

SANDBOX_COMMANDS = [
    ("s_tf", _("Simulate Transfer")),
    ("s_tfla", _("Simulate transfer ledger available")),
]


class PlaidTransferSandboxSimulationWizard(models.TransientModel):
    _name = "plaid.transfer.sandbox.simulation.wizard"

    command = fields.Selection(
        selection=SANDBOX_COMMANDS, string="Command", required=True
    )

    transfer_id = fields.Many2one("plaid.transfer", string="Transfer")
    event_type = fields.Selection(
        [
            ("failed", _("Failure")),
            ("posted", _("Posted")),
            ("settled", _("Success")),
        ]
    )
    failure_reason = fields.Char(string="Failure Reason", default=" ")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.user.company_id.id
    )

    def action_confirm(self):
        PlaidInterface = self.env["plaid.interface"]
        client = PlaidInterface._client(
            self.company_id.plaid_client_id,
            self.company_id.plaid_secret,
            self.company_id.plaid_host,
        )

        if self.command == "s_tf":
            PlaidInterface._sandbox_simulate_transfer(
                client, self.transfer_id.name, self.event_type, self.failure_reason
            )

        if self.command == "s_tfla":
            PlaidInterface._sandbox_transfer_ledger_simulate_available(client)
