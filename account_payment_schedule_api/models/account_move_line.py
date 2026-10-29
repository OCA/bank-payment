# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.account_payment_order_api.models.account_payment_api_line import (
    LINE_STATES,
)

# A pending line of a batch in one of these states may have reached the bank.
UNKNOWN_BATCH_STATES = ("sending", "uncertain")
REFUSED_STATES = ("refused", "rejected", "returned")


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    payment_schedule_bank_state = fields.Selection(
        selection=LINE_STATES,
        string="Bank Status",
        compute="_compute_payment_schedule_bank",
        search="_search_payment_schedule_bank_state",
        help="Status given by the bank to the last payment of this item sent "
        "through an API.",
    )
    payment_schedule_bank_reason = fields.Char(
        string="Bank Reason", compute="_compute_payment_schedule_bank"
    )

    @api.depends("payment_line_ids.api_line_ids.state")
    def _compute_payment_schedule_state(self):
        return super()._compute_payment_schedule_state()

    @staticmethod
    def _get_payment_schedule_bank_state(state, batch_state):
        if state == "pending" and batch_state in UNKNOWN_BATCH_STATES:
            return "unknown"
        return state

    @api.depends(
        "payment_line_ids.api_line_ids.state",
        "payment_line_ids.api_line_ids.reason",
        "payment_line_ids.api_line_ids.batch_id.state",
    )
    def _compute_payment_schedule_bank(self):
        api_lines = self.env["account.payment.api.line"].search(
            [("move_line_id", "in", self._origin.ids)], order="id desc"
        )
        last = {}
        for api_line in api_lines:
            last.setdefault(api_line.move_line_id.id, api_line)
        for line in self:
            api_line = last.get(line._origin.id)
            line.payment_schedule_bank_state = api_line and (
                self._get_payment_schedule_bank_state(
                    api_line.state, api_line.batch_id.state
                )
            )
            line.payment_schedule_bank_reason = api_line.reason if api_line else False

    def _search_payment_schedule_bank_state(self, operator, value):
        if operator not in ("=", "in"):
            raise UserError(_("Unsupported search on the bank status."))
        values = {value} if isinstance(value, str) else set(value or [])
        self.env["account.payment.api.line"].flush_model(
            ["move_line_id", "state", "batch_id"]
        )
        self.env["account.payment.api.batch"].flush_model(["state"])
        self.env.cr.execute(
            """
            SELECT DISTINCT ON (line.move_line_id)
                line.move_line_id, line.state, batch.state
            FROM account_payment_api_line line
            JOIN account_payment_api_batch batch ON batch.id = line.batch_id
            WHERE line.move_line_id IS NOT NULL
            ORDER BY line.move_line_id, line.id DESC
            """
        )
        ids = [
            move_line_id
            for move_line_id, state, batch_state in self.env.cr.fetchall()
            if self._get_payment_schedule_bank_state(state, batch_state) in values
        ]
        return [("id", "in", ids)]

    @api.model
    def _get_payment_schedule_dashboard_counters(self):
        return super()._get_payment_schedule_dashboard_counters() + [
            {
                "filter": "bank_awaiting_release",
                "label": _("Awaiting Release at the Bank"),
                "domain": [
                    ("reconciled", "=", False),
                    ("payment_schedule_bank_state", "=", "awaiting_release"),
                ],
            },
            {
                "filter": "bank_refused",
                "label": _("Refused by the Bank"),
                "domain": [
                    (
                        "payment_schedule_state",
                        "in",
                        ("to_schedule", "missing_instrument"),
                    ),
                    ("payment_schedule_bank_state", "in", REFUSED_STATES),
                ],
                "alert": True,
            },
            {
                "filter": "bank_unknown",
                "label": _("Outcome Unknown"),
                "domain": [
                    ("reconciled", "=", False),
                    ("payment_schedule_bank_state", "=", "unknown"),
                ],
                "alert": True,
            },
        ]
