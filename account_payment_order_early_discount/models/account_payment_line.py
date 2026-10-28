# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools.misc import format_amount, format_date


class AccountPaymentLine(models.Model):
    _inherit = "account.payment.line"

    # Core: related to the due date of the journal item; here the discount date
    # while the early payment discount can still be taken (see payment mode)
    ml_maturity_date = fields.Date(
        string="Due Date",
        related=None,
        compute="_compute_ml_maturity_date",
        readonly=True,
    )
    early_discount_date = fields.Date(
        related="move_line_id.discount_date", string="Discount Date"
    )
    early_discount_amount = fields.Monetary(
        string="Early Discount",
        currency_field="currency_id",
        readonly=True,
        help="Early payment discount deducted from the amount of this line.",
    )
    early_discount_residual = fields.Monetary(
        string="Open Amount for Early Discount",
        currency_field="currency_id",
        readonly=True,
        help="Open amount of the journal item when the amount of this line was "
        "computed. If the amount still matches it (minus the discount), the line is "
        "updated to the open amount and discount on confirmation.",
    )

    @api.depends(
        "move_line_id.date_maturity",
        "move_line_id.discount_date",
        "order_id.payment_mode_id",
    )
    def _compute_ml_maturity_date(self):
        for line in self:
            line.ml_maturity_date = (
                line.move_line_id._get_payment_order_maturity_date(
                    line.order_id.payment_mode_id
                )
                if line.move_line_id
                else False
            )

    def _update_early_discount(self):
        """Update the amount and early discount of lines of bills with an early
        discount to the open amount of the bill and the requested execution date,
        when confirming the order. Lines with a manually changed amount are left
        untouched and get no discount."""
        for line in self.filtered(
            lambda line: line.move_line_id
            and line.move_line_id._payment_order_has_early_discount()
        ):
            aml = line.move_line_id
            order = line.order_id
            currency = line.currency_id
            full = abs(aml.amount_residual_currency)
            amount = abs(line.amount_currency)
            computed = (
                line.early_discount_residual or full
            ) - line.early_discount_amount
            if currency.compare_amounts(amount, computed):
                if line.early_discount_amount:
                    line.early_discount_amount = 0.0
                continue
            date = order._get_early_discount_execution_date(aml)
            discount = aml._get_payment_order_early_discount(
                currency, date, order.payment_mode_id
            )
            if (
                not currency.compare_amounts(amount, full - discount)
                and not currency.compare_amounts(discount, line.early_discount_amount)
                and not currency.compare_amounts(line.early_discount_residual, full)
            ):
                continue
            sign = 1 if line.amount_currency >= 0 else -1
            had_discount = not currency.is_zero(line.early_discount_amount)
            line.write(
                {
                    "amount_currency": sign * (full - discount),
                    "early_discount_amount": discount,
                    "early_discount_residual": full,
                }
            )
            if discount and not had_discount:
                body = self.env._(
                    "Early discount of %(amount)s deducted for %(ref)s "
                    "(execution %(date)s).",
                    amount=format_amount(self.env, discount, currency),
                    ref=aml.move_id.display_name,
                    date=format_date(self.env, date),
                )
            elif not discount and had_discount:
                body = self.env._(
                    "Early discount period of %(ref)s has expired (execution "
                    "%(date)s, discount until %(deadline)s): the full amount is paid.",
                    ref=aml.move_id.display_name,
                    date=format_date(self.env, date),
                    deadline=format_date(
                        self.env,
                        aml._get_payment_order_early_discount_deadline(
                            order.payment_mode_id
                        )
                        or aml.discount_date,
                    ),
                )
            else:
                continue
            order.message_post(body=body)
