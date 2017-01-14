# -*- coding: utf-8 -*-
# © 2015-2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
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


class BankPaymentLine(models.Model):
    _inherit = 'bank.payment.line'

    @api.multi
    def reconcile_payment_lines(self):
        test_condition = (config['test_enable'] and
                          not self.env.context.get('test_connector'))
        if test_condition or self.env.context.get('no_connector'):
            return super(BankPaymentLine, self).reconcile_payment_lines()
        session = ConnectorSession.from_env(self.env)
        for bline in self:
            if all([pline.move_line_id for pline in bline.payment_line_ids]):
                reconcile_one_move.delay(session, bline._name, bline.id)


@job(default_channel='root.account_payment_transfer_reconcile_batch')
def reconcile_one_move(session, model_name, bank_payment_line_id):
    bline_model = session.env[model_name]
    bline = bline_model.browse(bank_payment_line_id)
    if bline.exists():
        bline.with_context(no_connector=True).reconcile()
    else:
        return _(u'Nothing to do because the record has been deleted')
