# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models

# Same rule as the core wizard: an item in one of these orders is already taken.
ACTIVE_ORDER_STATES = ("draft", "open", "generated")


class AccountPaymentLine(models.Model):
    _inherit = "account.payment.line"

    def _filter_payment_schedule_holding(self):
        """Payment lines that keep their journal item out of the schedule.

        Modules that release a line before its order closes (a payment refused by
        the bank, for instance) remove it here.
        """
        return self.filtered(
            lambda pl: pl.move_line_id and pl.state in ACTIVE_ORDER_STATES
        )
