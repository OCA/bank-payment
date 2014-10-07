# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account Payment Blocking module for OpenERP
#    Copyright (C) 2014 ACSONE SA/NV (http://acsone.eu)
#    @author Adrien Peiffer <adrien.peiffer@acsone.eu>
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

from openerp.osv import orm, fields


class account_invoice(orm.Model):
    _inherit = "account.invoice"

    def _get_move_line(self, cr, uid, invoice_id, context=None):
        return self.pool.get('account.move.line')\
            .search(cr, uid, [('account_id.type', 'in',
                              ['payable', 'receivable']),
                              ('invoice.id', '=', invoice_id)])

    def _set_move_blocked(self, cr, uid, ids, name, field_value, arg,
                          context=None):
        if isinstance(ids, (int, long)):
                ids = [ids]
        for invoice in self.browse(cr, uid, ids, context=context):
            if invoice.move_id.id:
                move_line_ids = self._get_move_line(cr, uid, invoice.id,
                                                    context=context)
                assert len(move_line_ids) == 1
                # work with account_constraints from OCA/AFT:
                context.update({'from_parent_object': True})
                self.pool.get('account.move.line')\
                    .write(cr, uid, move_line_ids, {'blocked': field_value},
                           context=context)

    def _get_move_blocked(self, cr, uid, ids, name, arg, context=None):
        res = {}
        if isinstance(ids, (int, long)):
                ids = [ids]
        for invoice in self.browse(cr, uid, ids, context=context):
            if invoice.move_id.id:
                move_line_ids = self._get_move_line(cr, uid, invoice.id,
                                                    context=context)
                assert len(move_line_ids) == 1
                move_line = self.pool.get('account.move.line')\
                    .browse(cr, uid, move_line_ids, context=context)[0]
                res[invoice.id] = move_line.blocked
            else:
                res[invoice.id] = False
        return res

    _columns = {
        'blocked': fields.function(_get_move_blocked,
                                   fnct_inv=_set_move_blocked,
                                   type='boolean', string='No Follow Up',
                                   states={'draft': [('readonly',
                                                      True)]}),
    }
