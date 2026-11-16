# Copyright 2026 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

from odoo import fields, models


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    def draft2open(self):
        for order in self.filtered(lambda order: order.payment_type == "outbound"):
            order._add_preferred_supplier_bills()
        return super().draft2open()

    def _add_preferred_supplier_bills(self):
        """Put the bills of preferred suppliers due for early payment on the pay date.

        A preferred supplier is paid on its early payment date, not on its
        credit term: the bills that come along are those, and only those,
        whose early payment falls on the business day the order pays on. An
        early payment date on a weekend or a holiday is paid the business day
        before, so those bills come along on that day. The payment mode of
        the bill has to be the one of the order, as for any other bill.
        """
        self.ensure_one()
        pay_date = self.date_scheduled or fields.Date.context_today(self)
        lines = self.env["account.move.line"].search(
            [
                ("company_id", "=", self.company_id.id),
                ("move_id.move_type", "=", "in_invoice"),
                ("move_id.state", "=", "posted"),
                ("account_id.account_type", "=", "liability_payable"),
                ("reconciled", "=", False),
                ("partner_id.preferred_supplier", "=", True),
                ("payment_mode_id", "=", self.payment_mode_id.id),
                # A weekend or a holiday bridge shifts the pay date back a
                # few days at most; the window bounds the calendar look-ups.
                ("move_id.early_payment_date", ">=", pay_date),
                ("move_id.early_payment_date", "<=", pay_date + timedelta(days=7)),
            ]
        )
        lines = lines.filtered(
            lambda line: line.move_id._early_payment_pay_date() == pay_date
            and not line.payment_line_ids.filtered(
                lambda payment: payment.state in ("draft", "open", "generated")
            )
        )
        if not lines:
            return
        for move in lines.move_id.filtered(
            lambda move: move._early_payment_applies_on(pay_date)
        ):
            move.action_apply_early_payment()
        lines.create_payment_line_from_move_line(self)
