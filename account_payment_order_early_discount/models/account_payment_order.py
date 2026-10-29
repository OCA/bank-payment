# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    def _get_early_discount_execution_date(self, move_line):
        """Requested execution date of a payment line for `move_line`, computed like
        draft2open does."""
        self.ensure_one()
        today = fields.Date.context_today(self)
        if self.date_prefered == "due":
            date = move_line._get_payment_order_maturity_date(self.payment_mode_id)
        elif self.date_prefered == "fixed":
            date = self.date_scheduled
        else:
            date = today
        return max(date or today, today)

    def draft2open(self):
        # Before the payments are created and the totals are checked: update the
        # early discount of the lines to the execution date draft2open will set
        self.payment_line_ids._update_early_discount()
        return super().draft2open()

    def open2generated(self):
        # Before the file asks the bank to pay the confirmed amounts
        self.payment_line_ids._check_early_discount_before_file()
        return super().open2generated()
