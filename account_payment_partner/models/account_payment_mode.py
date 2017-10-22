# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, api, _
from odoo.exceptions import ValidationError


class AccountPaymentMode(models.Model):
    _inherit = "account.payment.mode"

    @api.constrains('company_id')
    def account_invoice_company_constrains(self):
        for mode in self:
            if self.env['account.invoice'].sudo().search(
                    [('payment_mode_id', '=', mode.id),
                     ('company_id', '!=', mode.company_id.id)], limit=1):
                raise ValidationError(_(
                    "You cannot change the Company. There exists "
                    "at least one Invoice with this Payment Mode, "
                    "already assigned to another Company."))

    @api.constrains('company_id')
    def account_move_line_company_constrains(self):
        for mode in self:
            if self.env['account.move.line'].sudo().search(
                    [('payment_mode_id', '=', mode.id),
                     ('company_id', '!=', mode.company_id.id)], limit=1):
                raise ValidationError(_(
                    "You cannot change the Company. There exists "
                    "at least one Journal Item with this Payment Mode, "
                    "already assigned to another Company."))
