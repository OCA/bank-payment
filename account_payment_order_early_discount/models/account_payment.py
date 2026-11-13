# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command, models
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def _prepare_payment_order_early_discount_lines(self, paylines):
        """Write-off lines for the early discount of `paylines` (invoices and credit
        notes), built like in the "Register Payment" wizard."""
        self.ensure_one()
        company = self.company_id
        if not (
            company.account_journal_early_pay_discount_gain_account_id
            and company.account_journal_early_pay_discount_loss_account_id
        ):
            raise UserError(
                self.env._(
                    "Set the cash discount gain and loss accounts in the accounting "
                    "settings of %(company)s to book early payment discounts.",
                    company=company.display_name,
                )
            )
        lines = []
        for payline in paylines:
            aml = payline.move_line_id
            discount = aml._get_payment_order_early_discount(
                self.currency_id, payline.date, payline.order_id.payment_mode_id
            )
            if self.currency_id.compare_amounts(
                discount, payline.early_discount_amount
            ):
                raise UserError(
                    self.env._(
                        "The early discount of %(ref)s can no longer be applied "
                        "(paid in the meantime or discount period over). Set the "
                        "payment order back to draft and confirm it again.",
                        ref=aml.move_id.display_name,
                    )
                )
            lines += aml._get_payment_order_early_discount_lines(discount)
        return lines

    def _generate_payment_order_early_discount_entry(self, paylines):
        self.ensure_one()
        write_off_line_vals = self._prepare_payment_order_early_discount_lines(paylines)
        if not self.move_id:
            self._generate_journal_entry(write_off_line_vals=write_off_line_vals)
            return
        line_vals = self._prepare_move_line_default_vals(
            write_off_line_vals=write_off_line_vals
        )
        self.move_id.with_context(skip_account_move_synchronization=True).write(
            {"line_ids": [Command.clear()] + [Command.create(v) for v in line_vals]}
        )

    def action_post(self):
        # Book the early discount (with tax correction) in the payment entry, like
        # the "Register Payment" wizard, so the invoice is fully reconciled; also
        # when a payment of an order is posted on its own
        for payment in self.filtered(lambda p: p.state == "draft"):
            paylines = payment.payment_line_ids.filtered(
                lambda line: line.move_line_id
                and not line.currency_id.is_zero(line.early_discount_amount)
            )
            if paylines:
                payment._generate_payment_order_early_discount_entry(paylines)
        return super().action_post()
