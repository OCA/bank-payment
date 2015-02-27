# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account Payment that pays invoices module for OpenERP
#    Copyright (C) 2015 VisionDirect (http://www.visiondirect.co.uk)
#    @author Matthieu Choplin <matthieu.choplin@visiondirect.co.uk>
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
from openerp.osv import osv


class payment_order_create(osv.osv_memory):
    _inherit = 'payment.order.create'

    def filter_lines_ids(self, cr, uid, line_ids):
        """
        :param cr: cursor of the database
        :param uid: user id
        :param line_ids: account_move_line records
        :return: updated list of line_ids that we want to pay
        """
        line_obj = self.pool.get('account.move.line')
        updated_line_ids = []
        payment_line = self.pool.get('payment.line')
        # we do not want to select the account_move_line that
        # have already been selected in non canceled payment orders.
        payment_line_ids = payment_line.search(cr, uid, [])
        move_line_ids = [
            line.move_line_id.id
            for line in payment_line.browse(cr, uid, payment_line_ids)
            if line.order_id.state != 'cancel'
            and line.move_line_id.invoice.state == 'paid'
        ]
        for line in line_obj.browse(cr, uid, line_ids):
            if line.id in move_line_ids:
                continue
            if not line.statement_id:
                updated_line_ids.append(line.id)
        return updated_line_ids

    def search_entries(self, cr, uid, ids, context=None):
        res = super(
            payment_order_create, self).search_entries(
            cr, uid, ids, context
            )
        line_ids = res['context']['line_ids']
        res['context']['line_ids'] = self.filter_lines_ids(cr, uid, line_ids)
        return res
