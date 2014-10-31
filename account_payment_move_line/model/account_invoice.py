# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account Payment Move Line module for OpenERP
#    Copyright (C) 2014 KMEE (http://www.kmee.com.br)
#    @author Luis Felipe Miléo <mileo@kmee.com.br>
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


class AccountInvoice(orm.Model):
    _inherit = 'account.invoice'

    # def finalize_invoice_move_lines(self, cr, uid, invoice_browse,
    #                                 move_lines):
    #     '''
    #     Can be like that instead of action_move_create
    #     '''
    #     for line in move_lines:
    #         if line[2]['account_id'] == invoice_browse.account_id.id:
    #             line[2]['payment_mode_id'] = \
    #                 invoice_browse.payment_mode_id.id
    #     return move_lines

    def action_move_create(self, cr, uid, ids, context=None):
        '''
        Copy from OCA/account_payment/account_payment_extension
        '''
        result = super(AccountInvoice, self).action_move_create(
            cr, uid, ids, context)
        if result:
            for inv in self.browse(cr, uid, ids, context):
                move_line_ids = []
                for move_line in inv.move_id.line_id:
                    if (move_line.account_id.type == 'receivable' or
                       move_line.account_id.type == 'payable') and \
                        move_line.state != 'reconciled' and \
                            not move_line.reconcile_id.id:
                        move_line_ids.append(move_line.id)
                if len(move_line_ids) and inv.payment_mode_id:
                    aml_obj = self.pool.get("account.move.line")
                    aml_obj.write(cr, uid, move_line_ids,
                                  {'payment_mode_id': inv.payment_mode_id.id})
        return result
