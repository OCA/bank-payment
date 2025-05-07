# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from markupsafe import Markup

from odoo import fields, models


class CancelVoidPaymentLine(models.TransientModel):
    _name = "cancel.void.payment.line"
    _description = "Void Payment Line"

    reason = fields.Text(
        string="Reason for the cancel",
    )

    def cancel_payment_line_entry(self):
        account_payment_line = self.env["account.payment.line"].browse(
            self._context.get("active_id")
        )
        moves_to_reverse = account_payment_line.payment_ids.move_id
        move_lines = moves_to_reverse.line_ids
        for move_line in move_lines:
            if move_line.partner_id == account_payment_line.partner_id:
                move_line.remove_move_reconcile()
        today = fields.Date.context_today(self)
        reversal_vals_list = []
        for move in moves_to_reverse:
            reversal_vals_list.append(
                move.with_context(include_business_fields=True).copy_data(
                    {
                        "date": today,
                        "invoice_date": today,
                        "journal_id": move.journal_id.id,
                        "ref": (self.env._("Reversal of: %s", move.name)),
                        "move_type": "entry",
                        "partner_id": move.partner_id.id,
                    }
                )[0]
            )
        reversed_move = self.env["account.move"].create(reversal_vals_list)
        for acm_line in reversed_move.line_ids.with_context(check_move_validity=False):
            acm_line.write(
                {
                    "debit": acm_line.credit,
                    "credit": acm_line.debit,
                    "amount_currency": -acm_line.amount_currency,
                }
            )
        reversed_move.env.flush_all()

        unlink_ids = reversed_move.line_ids.filtered(
            lambda line: line.partner_id != account_payment_line.partner_id
        )
        debit = sum(unlink_ids.mapped("debit"))
        credit = sum(unlink_ids.mapped("credit"))

        total = abs(debit - credit)
        journal = reversed_move.journal_id
        payment_line_id = reversed_move.line_ids.filtered(
            lambda line: line.account_id
            in journal._get_journal_outbound_outstanding_payment_accounts()
            and line.debit > 0.0
        )
        if payment_line_id:
            new_amount = abs(payment_line_id.debit - total)
            reversed_move.write(
                {
                    "line_ids": [
                        (3, unlink_ids.ids),
                        (1, payment_line_id.id, {"debit": new_amount, "credit": 0.0}),
                    ]
                }
            )

        reversed_move.action_post()

        for payment_line in account_payment_line:
            payment_line.write(
                {
                    "is_voided": True,
                    "void_date": today,
                    "void_reason": self.reason,
                }
            )
        account_payment_line.write(
            {
                "is_voided": True,
                "void_date": today,
                "void_reason": self.reason,
            }
        )
        account_payment_line.order_id.message_post(
            body=Markup(
                self.env._(
                    "Voiding Date: %(void_date)s <br> Partner: %(partner_name)s <br> \
                Total Amount: %(total_amount)s <br> Invoice Ref #: %(invoice_ref)s \
                <br> Void Reason: %(void_reason)s",
                    void_date=account_payment_line.void_date,
                    partner_name=account_payment_line.partner_id.name,
                    total_amount=account_payment_line.amount_currency,
                    invoice_ref=account_payment_line.communication,
                    void_reason=account_payment_line.void_reason,
                )
            )
        )
        for payment_line in account_payment_line:
            payment_line.move_line_id.move_id.message_post(
                body=Markup(
                    self.env._(
                        "Void Reason: %(void_reason)s <br> Void Date: %(void_date)s",
                        void_reason=account_payment_line.void_reason,
                        void_date=account_payment_line.void_date,
                    )
                )
            )
