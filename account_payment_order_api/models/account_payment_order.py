# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .account_payment_api_line import FINAL_STATES


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    _api_second_factor_methods = ("_api_send_to_bank",)

    api_provider = fields.Selection(related="payment_mode_id.api_provider")
    api_confirmed_user_id = fields.Many2one(
        comodel_name="res.users", copy=False, groups=fields.NO_ACCESS
    )
    api_batch_ids = fields.One2many(
        comodel_name="account.payment.api.batch",
        inverse_name="order_id",
        string="Bank Batches",
        readonly=True,
    )
    api_line_ids = fields.One2many(
        comodel_name="account.payment.api.line",
        inverse_name="order_id",
        string="Lines Sent to the Bank",
        readonly=True,
    )
    api_can_send = fields.Boolean(compute="_compute_api_state")
    api_state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("open", "Approved"),
            ("sending", "Sending"),
            ("tracking", "Waiting for the Bank"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        compute="_compute_api_state",
        string="Bank Status",
    )

    @api.depends("state", "api_batch_ids.state")
    def _compute_api_state(self):
        for order in self:
            batches = order.api_batch_ids
            order.api_can_send = bool(
                order.api_provider
                and order.state == "open"
                and (not batches or any(b.state == "draft" for b in batches))
            )
            if order.state in ("draft", "cancel"):
                order.api_state = order.state
            elif order.state == "uploaded":
                order.api_state = "done"
            elif not batches:
                order.api_state = "open"
            elif any(b.state in ("draft", "sending", "uncertain") for b in batches):
                order.api_state = "sending"
            else:
                order.api_state = "tracking"

    def _check_not_api(self):
        if self.filtered("api_provider"):
            raise UserError(
                _(
                    "Orders sent through a bank API have no payment file: use Send to Bank."
                )
            )

    def write(self, vals):
        locked = [name for name in ("payment_mode_id", "journal_id") if name in vals]
        if locked:
            new_mode = self.env["account.payment.mode"].browse(
                vals.get("payment_mode_id") or ()
            )
            for order in self.filtered(lambda o: o.state != "draft"):
                if any(order[name].id != vals[name] for name in locked) and (
                    order.api_provider or new_mode.api_provider
                ):
                    raise UserError(
                        _(
                            "Payment order %s is already confirmed: a bank API order "
                            "cannot change its payment mode or bank journal.",
                            order.name,
                        )
                    )
        if vals.get("state") in ("draft", "cancel"):
            self._api_check_nothing_sent()
        res = super().write(vals)
        if "state" in vals:
            api_orders = self.filtered("api_provider")
            api_orders.sudo().write(
                {
                    "api_confirmed_user_id": self.env.uid
                    if vals["state"] == "open"
                    else False
                }
            )
            if vals["state"] == "draft":
                api_orders.payment_ids.filtered(
                    lambda p: p.state == "draft"
                ).action_cancel()
        return res

    def _api_check_lines_editable(self):
        for order in self:
            if order.api_provider and order.state != "draft":
                raise UserError(
                    _(
                        "Payment order %s is not in draft: its payment lines "
                        "cannot change.",
                        order.name,
                    )
                )

    def open2generated(self):
        self._check_not_api()
        return super().open2generated()

    def generated2uploaded(self):
        self._check_not_api()
        return super().generated2uploaded()

    def _api_check_nothing_sent(self):
        for order in self.filtered("api_provider"):
            if any(state != "pending" for state in order.api_line_ids.mapped("state")):
                raise UserError(
                    _(
                        "Payment order %s was already sent to the bank: cancel its "
                        "lines at the bank instead.",
                        order.name,
                    )
                )

    def _api_check_user_can_act(self):
        """Batches and lines are written with sudo: the bank calls stay limited to
        who can write on the order."""
        self.check_access_rights("write")
        self.check_access_rule("write")

    def _api_check_can_send(self):
        for order in self:
            if not order.api_can_send or not order.payment_line_ids:
                raise UserError(
                    _("Payment order %s has nothing to send to the bank.", order.name)
                )
            sent = order.api_batch_ids.filtered(lambda b: b.state != "draft")
            for payline in order.payment_line_ids - sent.line_ids.payment_line_id:
                if "draft" not in payline.payment_ids.mapped("state"):
                    raise UserError(
                        _(
                            "Payment order %s has lines without a draft payment: "
                            "cancel it and confirm it again.",
                            order.name,
                        )
                    )

    def _api_second_factor_orders(self):
        return self

    def action_api_send(self):
        self._api_check_user_can_act()
        self._api_check_can_send()
        return self.env["account.payment.api.second.factor"]._run_after_check(
            self,
            "_api_send_to_bank",
            required=any(self.mapped("payment_mode_id.api_require_second_factor")),
        )

    def _api_send_to_bank(self):
        """Send the batches never sent. A batch still in draft never reached the
        bank (the reservation failed or was not tried), so sending it again is safe."""
        self._api_check_user_can_act()
        self._api_check_can_send()
        batch_model = self.env["account.payment.api.batch"]
        for order in self:
            batch_ids = (
                order.api_batch_ids.filtered(lambda b: b.state == "draft").ids
                or order._api_create_batches()
            )
            for batch in batch_model.browse(batch_ids):
                batch._api_send()
        return {"type": "ir.actions.client", "tag": "reload"}

    def action_api_check(self):
        self._api_check_user_can_act()
        for batch in self.api_batch_ids.filtered(
            lambda b: b.state in ("sending", "sent", "uncertain")
        ):
            batch._api_check()
        return {"type": "ir.actions.client", "tag": "reload"}

    def _api_create_batches(self):
        """Create the batches in a committed transaction before any bank call."""
        self.ensure_one()
        batch_model = self.env["account.payment.api.batch"]
        groups = {}
        for payline in self.payment_line_ids:
            key = batch_model._api_batch_key(self.api_provider, payline)
            groups.setdefault(key, []).append(payline.id)
        with self.env.registry.cursor() as cr:
            env = self.env(cr=cr)
            batch_ids = [
                env["account.payment.api.batch"]
                .sudo()
                .create(
                    {
                        "order_id": self.id,
                        "batch_key": key,
                        "line_ids": [
                            (0, 0, {"payment_line_id": pid}) for pid in payline_ids
                        ],
                    }
                )
                .id
                for key, payline_ids in groups.items()
            ]
        self.env.invalidate_all()
        return batch_ids

    def _api_update_state(self):
        """Close the order once the bank gave a final answer for every line."""
        for order in self.filtered(lambda o: o.api_provider and o.state == "open"):
            states = order.api_line_ids.mapped("state")
            if states and all(state in FINAL_STATES for state in states):
                order.write(
                    {
                        "state": "uploaded",
                        "date_uploaded": fields.Date.context_today(order),
                    }
                )
