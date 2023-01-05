# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import _, fields, models


class CancelVoidPaymentLine(models.TransientModel):
    _name = "cancel.void.payment.line"
    _description = "Void Payment Line"

    reason = fields.Text(
        string="Reason for the cancel",
    )

    def cancel_payment_line_entry(self):
        bank_payment = self.env["bank.payment.line"].browse(
            self._context.get("active_id")
        )
        partner_id = False
        moves_vals_list = []
        for move_line in bank_payment.order_id.move_ids.line_ids:
            if move_line.partner_id == bank_payment.partner_id:
                partner_id = move_line.partner_id
                move_line.remove_move_reconcile()
        move_id = bank_payment.order_id.move_ids
        new_move_date = date.today()
        moves_vals_list.append(
            move_id.with_context(include_business_fields=True).copy_data(
                {
                    "date": new_move_date,
                    "invoice_date": new_move_date,
                    "journal_id": move_id.journal_id.id,
                    "ref": (_("Reversal of: %s")) % (move_id.name),
                    "move_type": "in_refund",
                    "partner_id": partner_id.id,
                }
            )[0]
        )
        reversed_move = self.env["account.move"].create(moves_vals_list)
        for acm_line in reversed_move.line_ids.with_context(check_move_validity=False):
            acm_line.write(
                {
                    "debit": acm_line.credit,
                    "credit": acm_line.debit,
                    "amount_currency": -acm_line.amount_currency,
                }
            )
        reversed_move.recompute()

        unlink_ids = self.env["account.move.line"].search(
            [
                ("partner_id", "!=", bank_payment.partner_id.id),
                ("move_id", "=", reversed_move.id),
            ]
        )
        debit = 0.0
        credit = 0.0
        for rec in unlink_ids:
            debit += rec.debit
            credit += rec.credit
        total = abs(debit - credit)
        journal = reversed_move.journal_id
        payment_line_id = self.env["account.move.line"].search(
            [
                ("move_id", "=", reversed_move.id),
                (
                    "account_id",
                    "=",
                    journal.company_id.account_journal_payment_credit_account_id.id,
                ),
                ("debit", ">", 0.0),
            ]
        )
        new_amount = abs(payment_line_id.debit - total)
        reversed_move.write(
            {
                "line_ids": [
                    (3, unlink_ids.ids),
                    (1, payment_line_id.id, {"debit": new_amount, "credit": 0.0}),
                ]
            }
        )

        # reconcile receivable/payable lines
        reconcile_lines = self.env["account.move.line"].search(
            [
                ("partner_id", "=", bank_payment.partner_id.id),
                ("move_id", "in", [move_id.id, reversed_move.id]),
                (
                    "account_id",
                    "!=",
                    move_id.journal_id.company_id.account_journal_payment_credit_account_id.id,
                ),
            ]
        )
        for line in reconcile_lines:
            if not line.account_id.reconcile:
                reconcile_lines -= line

        reversed_move.action_post()
        reconcile_lines.reconcile()

        for payment_line in bank_payment.payment_line_ids:
            payment_line.is_voided = True
            payment_line.void_date = date.today()
            payment_line.void_reason = self.reason
        bank_payment.is_voided = True
        bank_payment.void_date = date.today()
        bank_payment.void_reason = self.reason
        bank_payment.order_id.message_post(
            body=(
                _(
                    "Voiding Date: {} <br> Partner: {} <br> \
                    Total Amount: {} <br> Invoice Ref #: {} \
                    <br> Void Reason: {}"
                ).format(
                    bank_payment.void_date,
                    bank_payment.partner_id.name,
                    bank_payment.amount_currency,
                    bank_payment.communication,
                    bank_payment.void_reason,
                )
            )
        )
        for payment_line in bank_payment.payment_line_ids:
            payment_line.move_line_id.move_id.message_post(
                body=(
                    _("Void Reason: {} <br> Void Date: {}").format(
                        bank_payment.void_reason, bank_payment.void_date
                    )
                )
            )
