# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    mandate_id = fields.Many2one(
        'account.banking.mandate', string='Direct Debit Mandate',
        ondelete='restrict')

    @api.multi
    def _prepare_payment_line_vals(self, payment_order):
        vals = super(AccountMoveLine, self)._prepare_payment_line_vals(
            payment_order)
        if payment_order.payment_type == 'inbound' and self.mandate_id:
            vals['mandate_id'] = self.mandate_id.id
            vals['partner_bank_id'] = self.mandate_id.partner_bank_id.id
        return vals
