# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


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
        partner_bank_id = vals.get('partner_bank_id', False)
        if partner_bank_id and 'mandate_id' not in vals:
            mandate = self.env['account.banking.mandate'].search(
                [('partner_bank_id', '=', partner_bank_id),
                 ('state', '=', 'valid')], limit=1)
            if mandate:
                vals['mandate_id'] = mandate.id
        return vals
