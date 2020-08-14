# -*- coding: utf-8 -*-
# Copyright Akretion (http://www.akretion.com/)
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
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
        if payment_order.payment_type != 'inbound':
            return vals
        mandate = self.mandate_id
        partner_bank_id = False
        if not mandate and vals.get('mandate_id', False):
            mandate = mandate.browse(vals['mandate_id'])
        if not mandate:
            partner_bank_id = vals.get('partner_bank_id', False)
            if partner_bank_id:
                domain = [('partner_bank_id', '=', partner_bank_id)]
            else:
                domain = [('partner_id', '=', self.partner_id.id)]
            domain.append(('state', '=', 'valid'))
            mandate = mandate.search(domain, limit=1)
        vals.update({
            'mandate_id': mandate.id,
            'partner_bank_id': mandate.partner_bank_id.id or partner_bank_id,
        })
        return vals
