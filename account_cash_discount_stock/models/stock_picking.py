# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        res = super(StockPicking, self)\
            ._get_invoice_vals(key, inv_type, journal_id, move)
        if res.get('payment_term'):
            payment_term = self.env['account.payment.term']\
                .browse([res.get('payment_term')])
            res['discount_percent'] = payment_term.discount_percent
            res['discount_delay'] = payment_term.discount_delay
        return res
