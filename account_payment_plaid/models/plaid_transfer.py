import logging

from odoo import _, api, fields, models

TRANSFER_STATE = [
    ("cancelled", _("Cancelled")),
    ("pending", _("Pending")),
    ("failed", _("Failed")),
    ("posted", _("Posted")),
    ("settled", _("Completed")),
]

_logger = logging.getLogger(__name__)


class PlaidTransfer(models.Model):
    _name = "plaid.transfer"
    _order = "create_date desc"

    name = fields.Char(string="Name")
    description = fields.Char(string="Description")
    amount = fields.Float(string="Amount")
    state = fields.Selection(selection=TRANSFER_STATE, string="State")
    currency_id = fields.Many2one("res.currency", string="Currency")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.user.company_id.id,
    )
    host = fields.Selection(related="company_id.plaid_host", string="Host")
    ref = fields.Char(string="Reference")
    account_move_id = fields.Many2one("account.move", string="Account Move")

    def action_sandbox_simulation(self):
        return {
            "name": _("Plaid Transfer Sandbox Simulation"),
            "type": "ir.actions.act_window",
            "res_model": "plaid.transfer.sandbox.simulation.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_transfer_id": self.id,
                "default_company_id": self.company_id.id,
            },
        }

    @api.model
    def cron_sync_transfer_events(self):
        PlaidInterface = self.env["plaid.interface"]
        PaymentRegister = self.env["account.payment.register"].sudo()
        client = PlaidInterface._client(
            self.env.user.company_id.plaid_client_id,
            self.env.user.company_id.plaid_secret,
            self.env.user.company_id.plaid_host,
        )
        events = PlaidInterface._sync_transfer_events(client)

        events_per_type = {}
        for event in events:
            if event["event_type"] not in events_per_type.keys():
                events_per_type[event["event_type"]] = []

            if event["transfer_id"] not in [
                transfer
                for list_transfer in events_per_type.values()
                for transfer in list_transfer
            ]:
                events_per_type[event["event_type"]].append(event["transfer_id"])

        for event_type, events in events_per_type.items():
            transfer_ids = self.search(
                [("name", "in", events), ("state", "!=", "settled")]
            )

            if transfer_ids:
                transfer_ids.write({"state": event_type})
            if event_type == "settled":

                for transfer in transfer_ids:
                    PaymentRegister.with_context(
                        active_model="account.move",
                        active_ids=transfer.account_move_id.ids,
                        dont_redirect_to_payments=True,
                    ).create(
                        {
                            "payment_date": transfer.account_move_id.invoice_date,
                            "communication": transfer.account_move_id.name,
                            "amount": transfer.account_move_id.amount_total,
                            "payment_method_id": self.env.ref(
                                "account_payment_plaid.account_payment_method_plaid_out"
                            ).id,
                        }
                    ).action_create_payments()

        return True
