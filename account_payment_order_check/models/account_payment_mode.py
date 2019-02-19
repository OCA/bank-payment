# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountPaymentMode(models.Model):
    _inherit = 'account.payment.mode'

    check_layout_id = fields.Many2one(
        'account.payment.check.report',
        string='Check report',
    )

    @api.constrains('payment_method_id', 'check_layout_id')
    def check_layout(self):
        for rec in self:
            if (
                rec.payment_method_id.code == 'check_printing'
                and not rec.check_layout_id
            ):
                raise ValidationError(_(
                    'Layout is required for check printing'))
