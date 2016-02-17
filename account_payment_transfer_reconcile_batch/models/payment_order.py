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
    def _reconcile_payment_lines(self, bank_payment_lines):
        if config['test_enable'] or self.env.context.get('no_connector'):
            return super(PaymentOrder, self)._reconcile_payment_lines(
                bank_payment_lines)
        session = ConnectorSession.from_env(self.env)
        for bline in bank_payment_lines:
            reconcile_one_move.delay(session, bline._name, bline.id)


@job(default_channel='root.account_payment_transfer_reconcile_batch')
def reconcile_one_move(session, model_name, bank_payment_line_id):
    bline_model = session.env[model_name]
    bline = bline_model.browse(bank_payment_line_id)
    if bline.exists():
        obj = session.env['payment.order'].with_context(no_connector=True)
        obj._reconcile_payment_lines(bline)
    else:
        return _(u'Nothing to do because the record has been deleted')
