# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 ACSONE SA (<http://acsone.eu>).
#    Copyright (C) 2014 Akretion (www.akretion.com)
#
#    All other contributions are (C) by their respective contributors
#
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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
