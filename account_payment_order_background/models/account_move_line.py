# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, models
from odoo.addons.queue_job.job import job


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @job(default_channel='root.background.move_reconcile')
    @api.multi
    def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
        if self.env.context.get('__reconcile_as_job'):
            self.with_delay().reconcile(
                writeoff_acc_id=writeoff_acc_id,
                writeoff_journal_id=writeoff_journal_id,
            )
        else:
            try:
                super(AccountMoveLine, self).reconcile(
                    writeoff_acc_id=writeoff_acc_id,
                    writeoff_journal_id=writeoff_journal_id,
                )
            except exceptions.UserError as err:
                if self.env.context.get('job_uuid'):
                    # Processed in a job. We ignore failures, if they could
                    # not be reconciled it means it was already reconciled or
                    # not meant to be reconciled together (different accounts,
                    # company, ...). In such case a failed job would be useless.
                    return _('Not reconciled because of: %s') % (err.name,)
                raise
