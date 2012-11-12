# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2012 Therp BV (<http://therp.nl>).
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

from osv import osv, fields
class account_bank_statement_line(osv.osv):
    _inherit = 'account.bank.statement.line'
    def create_instant_voucher(self, cr, uid, ids, context=None):
        res = False
        if ids:
            if isinstance(ids, (int, float)):
                ids = [ids]
            if context is None:
                context = {}
            local_context = context.copy()
            context['active_id'] = ids[0]
            wizard_obj = self.pool.get('account.voucher.instant')
            res = {
                'name': wizard_obj._description,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': wizard_obj._name,
                'domain': [],
                'context': context,
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': False,
                'nodestroy': False,
                }
        return res
        
