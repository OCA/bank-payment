# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models
from openerp.models import expression


class PaymentOrderCreate(models.TransientModel):
    _inherit = 'account.payment.line.create'

    @api.multi
    def _prepare_move_line_domain(self):
        domain = super(PaymentOrderCreate, self)._prepare_move_line_domain()
        func = "openerp.addons.account_payment_transfer_reconcile_batch." \
               "models.bank_payment_line.reconcile_one_move(" \
               "'bank.payment.line',"
        jobs = self.env['queue.job'].sudo().search(
            [('func_string', 'like', "%s%%" % func), ('state', '!=', 'done')])
        if not jobs:
            return domain
        pline_ids = jobs.mapped(lambda x: int(x.func_string[len(func):-1]))
        # With this, we remove non existing records
        batch_domain = expression.AND([[('id', 'not in', pline_ids)], domain])
        return batch_domain
