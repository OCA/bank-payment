# Copyright 2026 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountPaymentLine(models.Model):
    _inherit = "account.payment.line"

    preferred_supplier = fields.Boolean(related="partner_id.preferred_supplier")
    # The date the order pays on when it pays "on due date": for a preferred
    # supplier that is the business day its early payment is paid on, while
    # it can still be earned, never its credit term. An order on a fixed
    # date keeps its date, as the payment order means it.
    ml_maturity_date = fields.Date(
        related=None,
        compute="_compute_ml_maturity_date",
        string="Maturity Date",
    )

    @api.depends(
        "move_line_id.date_maturity",
        "move_line_id.move_id.early_payment_date",
        "preferred_supplier",
    )
    def _compute_ml_maturity_date(self):
        today = fields.Date.context_today(self)
        for line in self:
            move = line.move_line_id.move_id
            early = move._early_payment_pay_date() if move else False
            if line.preferred_supplier and early and early >= today:
                line.ml_maturity_date = early
            else:
                line.ml_maturity_date = line.move_line_id.date_maturity

    @api.ondelete(at_uninstall=False)
    def _unlink_except_preferred_supplier(self):
        # A preferred supplier is preferred for paying its bills: once in the
        # order they stay, unless the user is allowed to take them out.
        preferred = self.filtered("preferred_supplier")
        if preferred and not self.env.user.has_group(
            "account_payment_order_early_payment_discount."
            "account_payment_line_group_remove_preferred"
        ):
            raise UserError(
                self.env._(
                    "The bills of a preferred supplier stay in the payment order: "
                    "%s. Only a user allowed to remove preferred suppliers can take "
                    "them out.",
                    ", ".join(preferred.partner_id.mapped("display_name")),
                )
            )
