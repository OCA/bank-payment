# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 ACSONE SA (<http://acsone.eu>).
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

from openerp.osv import orm
from openerp import workflow


class AccountMoveReconcile(orm.Model):

    _inherit = 'account.move.reconcile'

    def unlink(self, cr, uid, ids, context=None):
        """ workflow triggers upon unreconcile

        This should go into the core"""
        line_ids = []
        for reconcile in self.browse(cr, uid, ids, context=context):
            for move_line in reconcile.line_id:
                line_ids.append(move_line.id)
        res = super(AccountMoveReconcile, self).\
            unlink(cr, uid, ids, context=context)
        for line_id in line_ids:
            workflow.trg_trigger(uid, 'account.move.line', line_id, cr)
        return res
