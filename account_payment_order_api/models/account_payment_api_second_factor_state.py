# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountPaymentApiSecondFactorState(models.Model):
    _name = "account.payment.api.second.factor.state"
    _description = "Lockout and Last Used Code per User (no user access)"

    user_id = fields.Many2one(
        comodel_name="res.users", required=True, ondelete="cascade"
    )
    failures = fields.Integer()
    last_failure = fields.Datetime()
    last_counter = fields.Integer()

    _sql_constraints = [
        ("user_uniq", "unique(user_id)", "One second factor state per user."),
    ]
