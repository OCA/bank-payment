# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError

LINE_STATES = [
    ("pending", "Pending"),
    ("accepted", "Accepted"),
    ("awaiting_release", "Awaiting Release at the Bank"),
    ("scheduled", "Scheduled"),
    ("processing", "Processing"),
    ("paid", "Paid"),
    ("refused", "Refused"),
    ("rejected", "Rejected"),
    ("cancelled", "Cancelled"),
    ("returned", "Returned"),
    ("unknown", "Unknown"),
]
# The journal item of a line in one of these states can be paid again.
RELEASED_STATES = ("refused", "rejected", "cancelled", "returned")
FINAL_STATES = ("paid",) + RELEASED_STATES
CANCELLABLE_STATES = ("accepted", "awaiting_release", "scheduled")


class AccountPaymentApiLine(models.Model):
    _name = "account.payment.api.line"
    _description = "Payment Line Sent to a Bank API"
    _order = "batch_id, id"

    batch_id = fields.Many2one(
        comodel_name="account.payment.api.batch",
        required=True,
        ondelete="cascade",
        index=True,
    )
    order_id = fields.Many2one(related="batch_id.order_id", store=True, index=True)
    company_id = fields.Many2one(related="batch_id.company_id", store=True)
    payment_line_id = fields.Many2one(
        comodel_name="account.payment.line",
        required=True,
        ondelete="restrict",
        index=True,
    )
    move_line_id = fields.Many2one(related="payment_line_id.move_line_id", store=True)
    partner_id = fields.Many2one(related="payment_line_id.partner_id")
    amount = fields.Monetary(related="payment_line_id.amount_currency")
    currency_id = fields.Many2one(related="payment_line_id.currency_id")
    payment_id = fields.Many2one(
        comodel_name="account.payment",
        compute="_compute_payment_id",
        help="Draft payment created when the order was confirmed; it is only "
        "posted when the bank reports the line as paid.",
    )
    state = fields.Selection(selection=LINE_STATES, default="pending", required=True)
    bank_reference = fields.Char(copy=False, help="Identifier of the line at the bank")
    reason = fields.Char(help="Reason given by the bank for the current status")
    authentication = fields.Char(help="Authentication code given by the bank")
    date_paid = fields.Date(readonly=True)
    amount_paid = fields.Monetary(readonly=True)

    def _compute_payment_id(self):
        for line in self:
            line.payment_id = line.payment_line_id.payment_ids[:1]

    def action_api_cancel(self):
        """Ask the bank to cancel lines it has not executed yet."""
        self.order_id._api_check_user_can_act()
        lines = self.filtered(lambda x: x.state in CANCELLABLE_STATES)
        if not lines:
            raise UserError(
                _("Only lines the bank has not executed yet can be cancelled.")
            )
        for batch in lines.batch_id:
            batch._api_cancel_lines(lines.filtered(lambda x, b=batch: x.batch_id == b))
        return True

    def _api_apply(self, result):
        """Apply a normalized provider result to the line.

        ``result`` keys: state (one of LINE_STATES), and optionally
        bank_reference, reason, authentication, date, amount.
        """
        self.ensure_one()
        new_state = result.get("state") or self.state
        if new_state not in dict(LINE_STATES):
            raise UserError(_("Unknown payment status %s from the bank.") % new_state)
        if self.state in FINAL_STATES and self.state != "paid":
            return False
        if self.state == "paid" and new_state not in ("paid", "returned"):
            return False
        vals = {
            key: result[key]
            for key in ("bank_reference", "reason", "authentication")
            if result.get(key)
        }
        if new_state == "paid" and self.state != "paid":
            vals["date_paid"] = result.get("date") or fields.Date.context_today(self)
            vals["amount_paid"] = result.get("amount") or self.amount
            self._api_post_payment(vals["date_paid"])
        elif new_state in RELEASED_STATES and self.state != new_state:
            self._api_release_payment()
        vals["state"] = new_state
        self.sudo().write(vals)
        return True

    def _api_post_payment(self, date):
        payment = self.payment_id
        if not payment or payment.state == "posted":
            return
        payment.date = date
        payment.action_post()
        (
            self.move_line_id
            + payment.move_id.line_ids.filtered(
                lambda x: x.account_id == payment.destination_account_id
            )
        ).reconcile()

    def _api_release_payment(self):
        for payment in self.payment_id.filtered(lambda p: p.state != "cancel"):
            if payment.state == "posted":
                payment.action_draft()
            payment.action_cancel()
