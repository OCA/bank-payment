# Copyright 2019 ACSONE SA/NV
# Copyright 2022 Tecnativa - Pedro M. Baeza
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    payment_order_id = fields.Many2one(comodel_name="account.payment.order")
    payment_line_ids = fields.Many2many(comodel_name="account.payment.line")
    payment_line_date = fields.Date(compute="_compute_payment_line_date")
    # Compatibility with previous approach for returns - To be removed on v16
    old_bank_payment_line_name = fields.Char()

    def _get_default_journal(self):
        res = super()._get_default_journal()
        return res.filtered(lambda journal: not journal.inbound_payment_order_only)

    @api.depends(
        "payment_type",
        "journal_id.inbound_payment_method_ids",
        "journal_id.outbound_payment_method_ids",
    )
    def _compute_payment_method_fields(self):
        res = super()._compute_payment_method_fields()
        for pay in self:
            if pay.payment_type == "inbound":
                pay.available_payment_method_ids = (
                    pay.journal_id.inbound_payment_method_ids.filtered(
                        lambda m: not m.payment_order_only
                    )
                )
            else:
                pay.available_payment_method_ids = (
                    pay.journal_id.outbound_payment_method_ids.filtered(
                        lambda m: not m.payment_order_only
                    )
                )

            pay.hide_payment_method = (
                len(pay.available_payment_method_ids) == 1
                and pay.available_payment_method_ids.code == "manual"
            )
        return res

    @api.depends("payment_line_ids", "payment_line_ids.date")
    def _compute_payment_line_date(self):
        for item in self:
            item.payment_line_date = item.payment_line_ids[:1].date

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        """Overwrite date_maturity of the move_lines that are generated when related
        to a payment order.
        """
        vals_list = super()._prepare_move_line_default_vals(
            write_off_line_vals=write_off_line_vals
        )
        if not self.payment_order_id:
            return vals_list
        for vals in vals_list:
            vals["date_maturity"] = self.payment_line_ids[:1].date
        return vals_list
