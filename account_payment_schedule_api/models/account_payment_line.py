# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.account_payment_order_api.models.account_payment_api_line import (
    RELEASED_STATES,
)


class AccountPaymentLine(models.Model):
    _inherit = "account.payment.line"

    api_line_ids = fields.One2many(
        comodel_name="account.payment.api.line",
        inverse_name="payment_line_id",
        string="Lines Sent to the Bank API",
    )

    def _filter_payment_schedule_holding(self):
        """A line refused, rejected, cancelled or returned by the bank frees its
        item, even while the rest of the order is still at the bank (same rule as
        the payment line wizard of ``account_payment_order_api``)."""
        holding = super()._filter_payment_schedule_holding()
        return holding.filtered(
            lambda pl: not any(
                state in RELEASED_STATES for state in pl.api_line_ids.mapped("state")
            )
        )
