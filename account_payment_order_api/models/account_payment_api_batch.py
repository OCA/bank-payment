# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .account_payment_api_line import FINAL_STATES

_logger = logging.getLogger(__name__)

# A batch left in "sending" for longer than this was interrupted mid-call: its
# outcome is unknown and it is checked at the bank, never sent again.
SENDING_TIMEOUT = timedelta(minutes=15)


class PaymentApiResultUnknown(Exception):
    """Raised by a provider when the bank may or may not have the batch
    (timeout, connection lost after the request). The batch is checked later,
    never sent again."""


class AccountPaymentApiBatch(models.Model):
    _name = "account.payment.api.batch"
    _description = "Payment Batch Sent to a Bank API"
    _order = "id desc"

    name = fields.Char(compute="_compute_name")
    order_id = fields.Many2one(
        comodel_name="account.payment.order",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one(related="order_id.company_id", store=True)
    provider = fields.Selection(related="order_id.payment_mode_id.api_provider")
    batch_key = fields.Char(
        required=True,
        help="Provider key grouping the lines of one bank batch (for instance, "
        "the kind of payment)",
    )
    bank_reference = fields.Char(copy=False, help="Identifier of the batch at the bank")
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("sending", "Sending"),
            ("sent", "Sent"),
            ("uncertain", "Outcome Unknown"),
            ("failed", "Failed"),
        ],
        default="draft",
        required=True,
    )
    line_ids = fields.One2many(
        comodel_name="account.payment.api.line", inverse_name="batch_id"
    )
    date_sent = fields.Datetime(readonly=True)
    date_checked = fields.Datetime(readonly=True)
    message = fields.Text(readonly=True)

    def _compute_name(self):
        for batch in self:
            batch.name = "%s / %s" % (
                batch.order_id.name,
                batch.bank_reference or batch.batch_key,
            )

    def _api_second_factor_orders(self):
        return self.order_id

    # Provider dispatch -----------------------------------------------------

    def _api_call(self, operation, *args):
        """Call ``_api_<provider>_<operation>`` implemented by the provider module.

        - reserve(): returns the batch identifier at the bank, or False when the
          bank only gives it in the answer of send.
        - send() and query(): return {"bank_reference": str or False,
          "lines": {api_line_id: result}}, result as in
          ``account.payment.api.line._api_apply``.
        - cancel(api_lines): returns {"lines": {api_line_id: result}}.
        """
        self.ensure_one()
        method = getattr(self, "_api_%s_%s" % (self.provider, operation), None)
        if not method:
            raise UserError(
                _("Bank API provider %(provider)s does not implement %(op)s.")
                % {"provider": self.provider, "op": operation}
            )
        return method(*args)

    @api.model
    def _api_batch_key(self, provider, payment_line):
        method = getattr(self, "_api_%s_batch_key" % provider, None)
        return method(payment_line) if method else "default"

    def _api_apply_answer(self, answer):
        if answer.get("bank_reference"):
            self.sudo().bank_reference = answer["bank_reference"]
        for line in self.line_ids:
            result = (answer.get("lines") or {}).get(line.id)
            if result:
                line._api_apply(result)

    # Durable steps (each one in its own committed transaction) -------------

    def _api_send(self):
        """Reserve, mark as sending and send. Runs in dedicated cursors so the
        reservation and the "sending" mark survive a rollback of the caller.

        The batch is only read in those cursors: the caller's transaction may
        not see it (it can be created after the caller's snapshot)."""
        self.ensure_one()
        with self.env.registry.cursor() as cr:
            batch = self.with_env(self.env(cr=cr))
            if batch.state != "draft":
                return
            vals = {"state": "sending", "date_sent": fields.Datetime.now()}
            reference = batch._api_call("reserve")
            if reference:
                vals["bank_reference"] = reference
            batch.sudo().write(vals)
        with self.env.registry.cursor() as cr:
            self.with_env(self.env(cr=cr))._api_send_now()
        self.env.invalidate_all()

    def _api_send_now(self):
        try:
            answer = self._api_call("send")
        except PaymentApiResultUnknown as error:
            self.sudo().write({"state": "uncertain", "message": str(error)})
            return
        except Exception as error:  # pylint: disable=broad-except
            _logger.exception("Payment batch %s failed", self.name)
            self.sudo().write({"state": "failed", "message": str(error)})
            self.line_ids.sudo().write({"state": "refused", "reason": str(error)[:250]})
            self.line_ids._api_release_payment()
            self.order_id._api_update_state()
            return
        self.sudo().write({"state": "sent", "message": False})
        self._api_apply_answer(answer)
        self.order_id._api_update_state()

    def _api_check(self):
        """Ask the bank for the current status of the batch and its lines."""
        self.ensure_one()
        with self.env.registry.cursor() as cr:
            batch = self.with_env(self.env(cr=cr))
            try:
                answer = batch._api_call("query")
            except Exception as error:  # pylint: disable=broad-except
                _logger.warning("Payment batch %s check failed: %s", batch.name, error)
                batch.sudo().write(
                    {"date_checked": fields.Datetime.now(), "message": str(error)}
                )
                return
            batch.sudo().write(
                {
                    "state": "sent",
                    "date_checked": fields.Datetime.now(),
                    "message": False,
                }
            )
            batch._api_apply_answer(answer)
            batch.order_id._api_update_state()
        self.env.invalidate_all()

    def _api_cancel_lines(self, api_lines):
        self.ensure_one()
        answer = self._api_call("cancel", api_lines)
        self._api_apply_answer(answer)
        self.order_id._api_update_state()

    @api.model
    def _cron_api_check(self):
        stale = fields.Datetime.now() - SENDING_TIMEOUT
        batches = self.search(
            [
                "|",
                ("state", "in", ("sent", "uncertain")),
                "&",
                ("state", "=", "sending"),
                ("date_sent", "<", stale),
            ]
        )
        for batch in batches:
            if batch.state == "sent" and all(
                state in FINAL_STATES for state in batch.line_ids.mapped("state")
            ):
                continue
            batch._api_check()
