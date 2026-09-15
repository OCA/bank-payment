# Copyright 2026 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _prepare_payment_line_vals(self, payment_order):
        # The payment is proposed for the discounted amount: paying within
        # the early payment days takes the discount off the bill first, and
        # the residual the payment line is built on already carries it.
        move = self.move_id
        if move._early_payment_applies_on(
            payment_order.date_scheduled or fields.Date.context_today(self)
        ):
            move.action_apply_early_payment()
        return super()._prepare_payment_line_vals(payment_order)
