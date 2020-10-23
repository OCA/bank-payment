# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountPaymentConditionMixin(models.AbstractModel):
    _name = "account.payment.condition.mixin"
    _description = "Account Payment Condition Mixin"

    def _compute_show_payment_condition(self):
        for record in self:
            record.show_payment_condition = self.user_has_groups(
                'account_payment_condition.group_payment_condition'
            )

    payment_condition_id = fields.Many2one(
        comodel_name='account.payment.condition',
        string='Payment Condition',
        ondelete='restrict',
    )

    show_payment_condition = fields.Boolean(
        compute='_compute_show_payment_condition'
    )

    @api.onchange('payment_condition_id')
    def _onchange_payment_condition(self):
        if self.payment_condition_id:
            self.payment_mode_id = self.payment_condition_id.payment_mode_id
            self.payment_term_id = self.payment_condition_id.payment_term_id
