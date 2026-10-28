# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import timedelta

from odoo import Command, fields, models
from odoo.tools import float_compare

# Invoices and credit notes: a discount shown on a credit note reduces its deduction
EARLY_DISCOUNT_MOVE_TYPES = (
    "out_invoice",
    "out_receipt",
    "in_invoice",
    "in_receipt",
    "out_refund",
    "in_refund",
)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _payment_order_has_early_discount(self):
        """Payment term line of an invoice or credit note showing an early discount."""
        self.ensure_one()
        move = self.move_id
        return bool(
            self.display_type == "payment_term"
            and self.discount_date
            and self.amount_currency
            and move.move_type in EARLY_DISCOUNT_MOVE_TYPES
            and move.invoice_payment_term_id.early_discount
        )

    def _get_payment_order_full_early_discount(self):
        """Early discount of the whole line (positive, line currency)."""
        self.ensure_one()
        if not self._payment_order_has_early_discount():
            return 0.0
        return max(abs(self.amount_currency) - abs(self.discount_amount_currency), 0.0)

    def _get_payment_order_early_discount_rate(self):
        self.ensure_one()
        full = self._get_payment_order_full_early_discount()
        return full / abs(self.amount_currency) if full else 0.0

    def _get_payment_order_settled_discount_rate(self, counterpart, own_rate):
        """Discount rate of an amount settled with `counterpart`: a credit note (or
        invoice) takes away its own discount, none if it shows no discount; any other
        settlement (payment) the proportional discount of this line."""
        if counterpart.move_id.is_invoice(include_receipts=True):
            return counterpart._get_payment_order_early_discount_rate()
        return own_rate

    def _get_payment_order_open_early_discount(self):
        """Early discount still open on this line: the full discount minus the
        discount of the amounts already settled (credit notes, partial payments)."""
        self.ensure_one()
        full = self._get_payment_order_full_early_discount()
        if not full:
            return 0.0
        own_rate = self._get_payment_order_early_discount_rate()
        settled = 0.0
        for partial in self.matched_debit_ids:
            settled += partial.credit_amount_currency * (
                self._get_payment_order_settled_discount_rate(
                    partial.debit_move_id, own_rate
                )
            )
        for partial in self.matched_credit_ids:
            settled += partial.debit_amount_currency * (
                self._get_payment_order_settled_discount_rate(
                    partial.credit_move_id, own_rate
                )
            )
        discount = min(full - settled, abs(self.amount_residual_currency))
        return self.currency_id.round(max(discount, 0.0))

    def _get_payment_order_early_discount_lines(self, discount):
        """Write-off lines booking `discount` of this line, built with the helper of
        the "Register Payment" wizard and scaled to the open discount if the line is
        partially settled (the helper always books the full discount)."""
        self.ensure_one()
        move = self.move_id
        if move.move_type in ("in_refund", "out_refund"):
            return self._get_payment_order_refund_early_discount_lines(discount)
        company = move.company_id
        currency = self.currency_id
        result = self.env[
            "account.move"
        ]._get_invoice_counterpart_amls_for_early_payment_discount(
            [
                {
                    "aml": self,
                    "amount_currency": -self.amount_residual_currency,
                    "balance": -self.amount_residual,
                }
            ],
            0.0,
        )
        lines = [
            dict(vals)
            for key in ("base_lines", "tax_lines", "term_lines")
            for vals in result[key]
        ]
        paid_share = (
            abs(self.amount_residual_currency / move.amount_total)
            if move.amount_total
            else 0.0
        )
        full = self._get_payment_order_full_early_discount()
        if not lines or (
            not currency.compare_amounts(discount, full)
            and not float_compare(paid_share, 1.0, precision_digits=6)
        ):
            return lines
        factor = discount / full
        sign = 1 if sum(vals["amount_currency"] for vals in lines) >= 0 else -1
        rate = abs(self.balance / self.amount_currency) if self.amount_currency else 1.0
        target = {
            "amount_currency": sign * discount,
            "balance": company.currency_id.round(sign * discount * rate),
        }
        taxes = [vals for vals in lines if vals.get("tax_repartition_line_id")]
        bases = [vals for vals in lines if not vals.get("tax_repartition_line_id")]
        for field, cur in (
            ("amount_currency", currency),
            ("balance", company.currency_id),
        ):
            # The helper scaled the taxes by the open share of the line
            for vals in taxes:
                vals[field] = cur.round(vals[field] / (paid_share or 1.0) * factor)
            rest = target[field] - sum(vals[field] for vals in taxes)
            base_total = sum(vals[field] for vals in bases)
            for vals in bases:
                vals[field] = cur.round(
                    rest * vals[field] / base_total if base_total else rest / len(bases)
                )
            if bases:
                biggest = max(bases, key=lambda vals: abs(vals[field]))
                biggest[field] += target[field] - sum(vals[field] for vals in lines)
        return lines

    def _get_payment_order_early_discount_deadline(self, payment_mode):
        """Last execution date on which the early payment discount is still taken
        (discount date plus grace days, extended to the next working day), or False."""
        self.ensure_one()
        if self.display_type != "payment_term" or not self.discount_date:
            return False
        deadline = self.discount_date + timedelta(
            days=payment_mode.early_discount_grace_days
        )
        if payment_mode.early_discount_extend_to_workday:
            deadline = self.company_id._payment_order_shift_to_workday(deadline, 1)
        return deadline

    def _get_payment_order_early_discount_date(self, payment_mode):
        """Planned execution date to take the early payment discount: the discount
        date, moved to a working day (forward if the period is extended to the next
        working day, else backward). With buffer days the payment is planned that
        many days before the discount date, on the working day before."""
        self.ensure_one()
        buffer_days = payment_mode.early_discount_buffer_days
        if buffer_days:
            return self.company_id._payment_order_shift_to_workday(
                self.discount_date - timedelta(days=buffer_days), -1
            )
        step = 1 if payment_mode.early_discount_extend_to_workday else -1
        return self.company_id._payment_order_shift_to_workday(self.discount_date, step)

    def _get_payment_order_early_discount(self, currency, execution_date, payment_mode):
        """Positive early payment discount in `currency` when paying this line on
        `execution_date`, else 0. Read only (used in onchanges)."""
        self.ensure_one()
        deadline = self._get_payment_order_early_discount_deadline(payment_mode)
        if not deadline or not execution_date or execution_date > deadline:
            return 0.0
        if (
            not self._payment_order_has_early_discount()
            or self.move_id.currency_id != currency
        ):
            return 0.0
        discount = self._get_payment_order_open_early_discount()
        return discount if currency.compare_amounts(discount, 0.0) > 0 else 0.0

    def _get_payment_order_maturity_date(self, payment_mode):
        """Due date used by payment orders: the early discount date while the
        discount can still be taken and the payment mode pays on discount date."""
        self.ensure_one()
        if (
            payment_mode.early_discount_pay_on_discount_date
            and self.display_type == "payment_term"
            and self.discount_date
        ):
            today = fields.Date.context_today(self)
            deadline = self._get_payment_order_early_discount_deadline(payment_mode)
            if deadline >= today and self._get_payment_order_open_early_discount():
                return self._get_payment_order_early_discount_date(payment_mode)
        return self.date_maturity

    def _prepare_payment_line_vals(self, payment_order):
        vals = super()._prepare_payment_line_vals(payment_order)
        discount = 0.0
        vals["early_discount_residual"] = abs(vals["amount_currency"])
        if payment_order.payment_mode_id:
            currency = self.env["res.currency"].browse(vals["currency_id"])
            discount = self._get_payment_order_early_discount(
                currency,
                payment_order._get_early_discount_execution_date(self),
                payment_order.payment_mode_id,
            )
            if discount:
                sign = 1 if vals["amount_currency"] >= 0 else -1
                vals["amount_currency"] -= sign * discount
        vals["early_discount_amount"] = discount
        return vals

    def _get_payment_order_refund_early_discount_lines(self, discount):
        """Write-off lines giving back the discount shown on a credit note (the core
        helper only handles invoices): the credit note lines times the discount
        share, with the opposite sign, taxes as on invoices."""
        self.ensure_one()
        move = self.move_id
        company = move.company_id
        currency = self.currency_id
        account = (
            company.account_journal_early_pay_discount_gain_account_id
            if move.move_type == "in_refund"
            else company.account_journal_early_pay_discount_loss_account_id
        )
        share = discount / move.amount_total if move.amount_total else 0.0
        sign = 1 if self.amount_currency > 0 else -1
        target = {
            "amount_currency": sign * discount,
            "balance": company.currency_id.round(
                sign * discount * abs(self.balance / self.amount_currency)
            ),
        }
        common = {
            "partner_id": self.partner_id.id,
            "currency_id": currency.id,
            "display_type": "epd",
        }
        products = move.line_ids.filtered(lambda line: line.display_type == "product")
        included = (
            move.invoice_payment_term_id.early_pay_discount_computation == "included"
            and products.tax_ids
        )
        lines = []
        bases = {}

        def base_vals(taxes):
            return dict(
                common,
                name=self.env._("Early Payment Discount"),
                account_id=account.id,
                tax_ids=[Command.set(taxes.ids)],
                tax_tag_ids=[
                    Command.set(
                        taxes.invoice_repartition_line_ids.filtered(
                            lambda rep: rep.repartition_type == "base"
                        ).tag_ids.ids
                    )
                ],
                amount_currency=0.0,
                balance=0.0,
            )

        for line in products:
            taxes = line.tax_ids if included else self.env["account.tax"]
            vals = bases.setdefault(taxes, base_vals(taxes))
            vals["amount_currency"] -= line.amount_currency * share
            vals["balance"] -= line.balance * share
        if not bases:
            # No product lines: the whole discount on the discount account
            bases[self.env["account.tax"]] = base_vals(self.env["account.tax"])
        lines += bases.values()
        if included:
            for line in move.line_ids.filtered("tax_repartition_line_id"):
                rep = line.tax_repartition_line_id
                tax = rep.tax_id
                # Same mapping as inverse_tax_rep() in the core helper: the
                # distributions of invoices and credit notes match line by line
                # (constraint _validate_repartition_lines on account.tax)
                index = list(tax.refund_repartition_line_ids).index(rep)
                invoice_rep = tax.invoice_repartition_line_ids[index]
                lines.append(
                    dict(
                        common,
                        name=self.env._("Early Payment Discount (%s)", tax.name),
                        account_id=line.account_id.id,
                        tax_repartition_line_id=invoice_rep.id,
                        tax_ids=[Command.set(line.tax_ids.ids)],
                        tax_tag_ids=[Command.set(invoice_rep.tag_ids.ids)],
                        group_tax_id=line.group_tax_id.id,
                        amount_currency=-line.amount_currency * share,
                        balance=-line.balance * share,
                    )
                )
        for field, cur in (
            ("amount_currency", currency),
            ("balance", company.currency_id),
        ):
            for vals in lines:
                vals[field] = cur.round(vals[field])
            biggest = max(bases.values(), key=lambda vals: abs(vals[field]))
            biggest[field] += target[field] - sum(vals[field] for vals in lines)
        return lines
