# Copyright 2017 ForgeFlow S.L.
# Copyright 2018 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountPaymentMode(models.Model):
    _inherit = "account.payment.mode"

    show_bank_account = fields.Selection(
        selection=[
            ("full", "Full"),
            ("first", "First n chars"),
            ("last", "Last n chars"),
            ("no", "No"),
        ],
        string="Show bank account",
        default="full",
        help="Show in invoices partial or full bank account number",
    )
    show_bank_account_from_journal = fields.Boolean(string="Bank account from journals")
    show_bank_account_chars = fields.Integer(
        string="# of digits for customer bank account"
    )

    @api.constrains("company_id")
    def account_invoice_company_constrains(self):
        for mode in self:
            if (
                self.env["account.move"]
                .sudo()
                .search(
                    [
                        ("payment_mode_id", "=", mode.id),
                        ("company_id", "!=", mode.company_id.id),
                    ],
                    limit=1,
                )
            ):
                raise ValidationError(
                    _(
                        "You cannot change the Company. There exists "
                        "at least one Journal Entry with this Payment Mode, "
                        "already assigned to another Company."
                    )
                )

    @api.constrains("company_id")
    def account_move_line_company_constrains(self):
        for mode in self:
            if (
                self.env["account.move.line"]
                .sudo()
                .search(
                    [
                        ("payment_mode_id", "=", mode.id),
                        ("company_id", "!=", mode.company_id.id),
                    ],
                    limit=1,
                )
            ):
                raise ValidationError(
                    _(
                        "You cannot change the Company. There exists "
                        "at least one Journal Item with this Payment Mode, "
                        "already assigned to another Company."
                    )
                )
