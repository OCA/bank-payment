# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    def _get_early_discount_execution_date(self, move_line):
        """Expected execution date of a new payment line, as draft2open computes it."""
        self.ensure_one()
        today = fields.Date.context_today(self)
        if self.date_prefered == "due":
            date = move_line._get_payment_order_maturity_date(self.payment_mode_id)
        elif self.date_prefered == "fixed":
            date = self.date_scheduled
        else:
            date = today
        return max(date or today, today)

    def post_and_reconcile(self):
        # Book the early discount (with tax correction) in the payment entry, like
        # the "Register Payment" wizard, so the invoice is fully reconciled.
        for payment in self.payment_ids.filtered(lambda p: p.state == "draft"):
            paylines = payment.payment_line_ids.filtered(
                lambda line: not line.currency_id.is_zero(line.early_discount_amount)
            )
            if paylines:
                payment._generate_payment_order_early_discount_entry(paylines)
        return super().post_and_reconcile()
