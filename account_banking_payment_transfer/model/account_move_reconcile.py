# -*- coding: utf-8 -*-
# © 2014 ACSONE SA (<http://acsone.eu>).
# © 2014 Akretion (www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, workflow, api


class AccountMoveReconcile(models.Model):
    _inherit = 'account.move.reconcile'

    @api.multi
    def unlink(self):
        """
        Workflow triggers upon unreconcile. This should go into the core.
        """
        line_ids = []
        for reconcile in self:
            for move_line in reconcile.line_id:
                line_ids.append(move_line.id)
        res = super(AccountMoveReconcile, self).unlink()
        for line_id in line_ids:
            workflow.trg_trigger(
                self._uid, 'account.move.line', line_id, self._cr)
        return res
