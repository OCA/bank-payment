# -*- coding: utf-8 -*-
# (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import logging
from openerp import models, api, _
from openerp.tools import config

_logger = logging.getLogger(__name__)

try:
    from openerp.addons.connector.queue.job import job
    from openerp.addons.connector.session import ConnectorSession
except ImportError:
    _logger.debug('Can not `import connector`.')
    import functools

    def empty_decorator_factory(*argv, **kwargs):
        return functools.partial
    job = empty_decorator_factory


class PaymentOrder(models.Model):
    _inherit = 'payment.order'

    @api.multi
    def _reconcile_payment_lines(self, payment_lines):
        if config['test_enable']:
            return super(PaymentOrder, self)._reconcile_payment_lines(
                payment_lines)
        session = ConnectorSession(
            self.env.cr, self.env.uid, context=self.env.context)
        for line in payment_lines:
            if line.move_line_id:
                reconcile_one_move.delay(
                    session, 'payment.line', line.id)
            else:
                self.action_sent_no_move_line_hook(line)


@job(default_channel='root.account_payment_transfer_reconcile_batch')
def reconcile_one_move(session, model_name, payment_line_id):
    payment_line_pool = session.pool[model_name]
    if payment_line_pool.exists(session.cr, session.uid, payment_line_id):
        payment_line_pool.debit_reconcile(
            session.cr, session.uid, [payment_line_id])
    else:
        return _(u'Nothing to do because the record has been deleted')
