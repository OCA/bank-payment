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
        We recreate function to be able set
        'amount_currency': line.amount_residual_currency
        instead of
        'amount_currency': line.amount_to_pay
        To be compliant with multi currency
        Allready corrected in V8 but will not be corrected in V7
        """
        res = super(payment_order_create, self).create_payment(cr,
                                                               uid,
                                                               ids,
                                                               context=context)
        line_obj = self.pool.get('account.move.line')
        payment_obj = self.pool.get('payment.line')
        data = self.browse(cr, uid, ids, context=context)[0]
        line_ids = [entry.id for entry in data.entries]
        if not line_ids:
            return res
        # Finally populate the current payment with new lines:
        for line in line_obj.browse(cr, uid, line_ids, context=context):
            payment_line_id = payment_obj.search(cr, uid,
                                                 [('move_line_id',
                                                   '=',
                                                   line.id)],
                                                 context=context)
            if payment_line_id:
                payment_obj.write(
                    cr,
                    uid,
                    payment_line_id,
                    {'amount_currency': line.amount_residual_currency},
                    context=context
                    )

        return res
