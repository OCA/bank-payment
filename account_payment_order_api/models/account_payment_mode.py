# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class AccountPaymentMode(models.Model):
    _inherit = "account.payment.mode"

    api_provider = fields.Selection(
        selection=[],
        string="Bank API Provider",
        help="Payment orders of this mode are sent to the bank through this "
        "provider instead of a payment file. Each provider module adds its value.",
    )
    api_require_second_factor = fields.Boolean(
        string="Require Second Factor",
        help="Sending to the bank asks for a code from the user's authenticator app, "
        "once per action.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("api_provider"):
                vals["group_lines"] = False
        return super().create(vals_list)

    def _api_check_open_orders(self, vals):
        provider_changed = self.filtered(
            lambda m: "api_provider" in vals and m.api_provider != vals["api_provider"]
        )
        factor_removed = self.filtered(
            lambda m: m.api_require_second_factor
            and not vals.get("api_require_second_factor", True)
        )
        if not provider_changed and not factor_removed:
            return
        orders = (
            self.env["account.payment.order"]
            .sudo()
            .search(
                [
                    ("payment_mode_id", "in", (provider_changed | factor_removed).ids),
                    ("state", "=", "open"),
                ]
            )
        )
        for order in orders:
            if order.payment_mode_id in provider_changed or order.api_can_send:
                raise UserError(
                    _(
                        "Payment order %s is still open with this payment mode: "
                        "finish or cancel it before changing the bank API settings.",
                        order.name,
                    )
                )

    def write(self, vals):
        self._api_check_open_orders(vals)
        if vals.get("api_provider"):
            vals = dict(vals, group_lines=False)
        return super().write(vals)

    @api.onchange("api_provider")
    def _onchange_api_provider(self):
        if self.api_provider:
            self.group_lines = False

    @api.constrains("api_provider", "group_lines", "payment_type")
    def _check_api_provider(self):
        for mode in self.filtered("api_provider"):
            if mode.payment_type != "outbound":
                raise ValidationError(
                    _("Bank API providers only send outbound payments.")
                )
            if mode.group_lines:
                raise ValidationError(
                    _(
                        "Payment mode %s sends through a bank API: the bank answers "
                        "line by line, so payment lines cannot be grouped.",
                        mode.name,
                    )
                )
