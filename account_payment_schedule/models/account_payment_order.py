# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    payment_schedule_cash_warning = fields.Text(
        string="Cash Warning", compute="_compute_payment_schedule_cash_warning"
    )

    def _compute_payment_schedule_cash_warning(self):
        today = fields.Date.context_today(self)
        move_line_model = self.env["account.move.line"]
        for order in self:
            warning = False
            if order.state == "draft" and order.payment_type == "outbound":
                date = order.date_scheduled if order.date_prefered == "fixed" else None
                dates = {date or today}
                if order.date_prefered == "due":
                    dates = (
                        set(order.payment_line_ids.mapped("ml_maturity_date")) or dates
                    )
                # Consolidated, as on the schedule: receivables are not tied
                # to a journal.
                warning = move_line_model.with_company(
                    order.company_id
                )._get_payment_schedule_cash_warning(dates)
            order.payment_schedule_cash_warning = warning
