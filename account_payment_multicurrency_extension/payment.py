# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Vincent Renaville
#    Copyright 2014 Camptocamp SA
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


class payment_order_create(orm.TransientModel):

    _inherit = 'payment.order.create'

    def create_payment(self, cr, uid, ids, context=None):
        """
        We add is_multi_currency tag to be able set
        'amount_currency': line.amount_residual_currency
        instead of
        'amount_currency': line.amount_to_pay
        To be compliant with multi currency
        Already corrected in V8 but will not be corrected in V7
        """
        if context is None:
            context = {}
        ctx = context.copy()
        ctx.update({'is_multi_currency': True})
        return super(payment_order_create, self).create_payment(
            cr,
            uid,
            ids,
            context=ctx)


class payment_line(orm.Model):
    _inherit = 'payment.line'

    def create(self, cr, uid, vals, context=None):
        """In case of multi currency
        we use amount_residual_currency instead of amount_to_pay"""
        if context is None:
            context = {}
        if context.get('is_multi_currency'):
            account_move_line_obj = self.pool['account.move.line']
            move_line = account_move_line_obj.browse(
                cr,
                uid,
                vals['move_line_id'],
                context=context)
            vals['amount_currency'] = move_line.amount_residual_currency
        return super(payment_line, self).create(cr, uid, vals, context=context)
