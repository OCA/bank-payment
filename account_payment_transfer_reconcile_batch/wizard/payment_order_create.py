# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class PaymentOrderCreate(models.TransientModel):
    _inherit = 'payment.order.create'

    @api.multi
    def filter_lines(self, lines):
        """Filter move lines before proposing them for inclusion in the payment
        order (inherited). This one removes the move lines that aren't still
        being processed in the connector queue.

        :param lines: recordset of move lines
        :returns: list of move line ids
        """
        filtered_line_ids = super(PaymentOrderCreate, self).filter_lines(lines)
        func = "openerp.addons.account_payment_transfer_reconcile_batch." \
               "models.payment_order.reconcile_one_move('bank.payment.line', "
        jobs = self.env['queue.job'].sudo().search(
            [('func_string', 'like', "%s%%" % func), ('state', '!=', 'done')])
        if not jobs:
            return filtered_line_ids
        pline_ids = jobs.mapped(lambda x: int(x.func_string[len(func):-1]))
        # With this, we remove non existing records
        plines = self.env['bank.payment.line'].search(
            [('id', 'in', pline_ids)])
        to_exclude = plines.mapped('payment_line_ids.move_line_id')
        return [line_id for line_id in filtered_line_ids if
                line_id not in to_exclude.ids]
