# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import UserError
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
        "move_line_id.amount_residual_currency",
        "order_id.payment_mode_id.early_discount_pay_on_discount_date",
        "order_id.payment_mode_id.early_discount_extend_to_workday",
        "order_id.payment_mode_id.early_discount_grace_days",
        "order_id.payment_mode_id.early_discount_buffer_days",
        "order_id.payment_line_ids.move_line_id",
        "order_id.payment_line_ids.amount_currency",
        "amount_currency",
        "partner_id",
    )
    def _compute_ml_maturity_date(self):
        for line in self:
            aml = line.move_line_id
            mode = line.order_id.payment_mode_id
            date = aml._get_payment_order_maturity_date(mode) if aml else False
            if date and line.amount_currency < 0:
                date = min([date] + line._get_early_discount_dates_of_partner())
            line.ml_maturity_date = date

    def _get_early_discount_dates_of_partner(self):
        """Early discount dates of the other lines of the order for the same partner:
        a credit note is deducted from the first payment taking a discount (instead
        of being a payment of its own on its due date, which would be negative)."""
        self.ensure_one()
        mode = self.order_id.payment_mode_id
        dates = []
        for line in self.order_id.payment_line_ids:
            aml = line.move_line_id
            if (
                line != self
                and aml
                and line.amount_currency > 0
                and line.partner_id == self.partner_id
            ):
                date = aml._get_payment_order_maturity_date(mode)
                if date != aml.date_maturity:
                    dates.append(date)
        return dates

    @api.onchange("move_line_id")
    def _onchange_move_line_id_early_discount(self):
        if not self.move_line_id:
            self.early_discount_amount = 0.0
            self.early_discount_residual = 0.0

    def _update_early_discount(self):
        """Update the amount and early discount of lines of bills with an early
        discount to the open amount of the bill and the requested execution date,
        when confirming the order. Lines with a manually changed amount are left
        untouched and get no discount."""
        self.filtered(
            lambda line: not line.move_line_id and line.early_discount_amount
        ).early_discount_amount = 0.0
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
            # A line changed to another currency than the bill counts as manual
            if currency != aml.currency_id or currency.compare_amounts(
                amount, computed
            ):
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

    def _check_early_discount_before_file(self):
        """The payment file asks the bank to execute the lines on their date, or
        as soon as possible if it is past: the open amount and early discount the
        lines were confirmed with must still hold then."""
        today = fields.Date.context_today(self)
        for line in self.filtered(
            lambda line: line.move_line_id
            and line.move_line_id._payment_order_has_early_discount()
        ):
            aml = line.move_line_id
            currency = line.currency_id
            if currency != aml.currency_id or currency.compare_amounts(
                abs(line.amount_currency),
                line.early_discount_residual - line.early_discount_amount,
            ):
                continue  # manually changed amount
            discount = aml._get_payment_order_early_discount(
                currency, max(line.date or today, today), line.order_id.payment_mode_id
            )
            if currency.compare_amounts(
                abs(aml.amount_residual_currency), line.early_discount_residual
            ) or currency.compare_amounts(discount, line.early_discount_amount):
                raise UserError(
                    self.env._(
                        "The open amount or the early discount of %(ref)s has changed "
                        "since the payment order was confirmed (settled in the "
                        "meantime or discount period over at %(date)s). Set the "
                        "payment order back to draft and confirm it again.",
                        ref=aml.move_id.display_name,
                        date=format_date(self.env, max(line.date or today, today)),
                    )
                )
