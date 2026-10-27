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
        """Check the early discount against the requested execution date (`date`,
        set when confirming the order). Lines with a manually changed amount are
        left untouched and get no discount."""
        for line in self.filtered("move_line_id"):
            aml = line.move_line_id
            currency = line.currency_id
            full = abs(aml.amount_residual_currency)
            amount = abs(line.amount_currency)
            if currency.compare_amounts(amount, full) and currency.compare_amounts(
                amount, full - line.early_discount_amount
            ):
                if line.early_discount_amount:
                    line.early_discount_amount = 0.0
                continue
            discount = aml._get_payment_order_early_discount(
                currency, line.date, line.order_id.payment_mode_id
            )
            if not currency.compare_amounts(
                amount, full - discount
            ) and not currency.compare_amounts(discount, line.early_discount_amount):
                continue
            sign = 1 if line.amount_currency >= 0 else -1
            had_discount = not currency.is_zero(line.early_discount_amount)
            line.write(
                {
                    "amount_currency": sign * (full - discount),
                    "early_discount_amount": discount,
                }
            )
            if discount and not had_discount:
                body = self.env._(
                    "Early discount of %(amount)s deducted for %(ref)s "
                    "(execution %(date)s).",
                    amount=format_amount(self.env, discount, currency),
                    ref=aml.move_id.display_name,
                    date=format_date(self.env, line.date),
                )
            elif not discount and had_discount:
                body = self.env._(
                    "Early discount period of %(ref)s has expired (execution "
                    "%(date)s, discount until %(deadline)s): the full amount is paid.",
                    ref=aml.move_id.display_name,
                    date=format_date(self.env, line.date),
                    deadline=format_date(
                        self.env,
                        aml._get_payment_order_early_discount_deadline(
                            line.order_id.payment_mode_id
                        )
                        or aml.discount_date,
                    ),
                )
            else:
                continue
            line.order_id.message_post(body=body)

    def _prepare_account_payment_vals(self):
        # Called by draft2open after the execution date of the lines has been set
        self._update_early_discount()
        return super()._prepare_account_payment_vals()
