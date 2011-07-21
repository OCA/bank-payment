# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import datetime
from osv import osv
from account_banking.struct import struct
from account_banking.parsers import convert

today = datetime.date.today

def str2date(str):
    dt = convert.str2date(str, '%Y-%m-%d')
    return datetime.date(dt.year, dt.month, dt.day)

class payment_order_create(osv.osv_memory):
    _inherit = 'payment.order.create'

    def create_payment(self, cr, uid, ids, context=None):
        '''
        This method is a slightly modified version of the existing method on this
        model in account_payment.
        - pass the payment mode to line2bank()
        - allow invoices to create influence on the payment process: not only 'Free'
        references are allowed, but others as well
        - check date_to_pay is not in the past.
        '''

        order_obj = self.pool.get('payment.order')
        line_obj = self.pool.get('account.move.line')
        payment_obj = self.pool.get('payment.line')
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        line_ids = data['entries']
        if not line_ids:
            return {'type': 'ir.actions.act_window_close'}

        payment = order_obj.browse(cr, uid, context['active_id'], context=context)
        ### account banking
        # t = None
        # line2bank = line_obj.line2bank(cr, uid, line_ids, t, context)
        line2bank = line_obj.line2bank(cr, uid, line_ids, payment.mode.id, context)
        _today = today()
        ### end account banking

        ## Finally populate the current payment with new lines:
        for line in line_obj.browse(cr, uid, line_ids, context=context):
            if payment.date_prefered == "now":
                #no payment date => immediate payment
                date_to_pay = False
            elif payment.date_prefered == 'due':
                ### account_banking
                # date_to_pay = line.date_maturity
                date_to_pay = line.date_maturity and \
                           str2date(line.date_maturity) > _today\
                           and line.date_maturity or False
                ### end account banking
            elif payment.date_prefered == 'fixed':
                ### account_banking
                # date_to_pay = payment.date_planned
                date_to_pay = payment.date_planned and \
                           str2date(payment.date_planned) > _today\
                           and payment.date_planned or False
                ### end account banking

            ### account_banking
            state = communication2 = False
            communication = line.ref or '/'
            if line.invoice:
                if line.invoice.reference_type == 'structured':
                    state = 'structured'
                    communication = line.invoice.reference
                else:
                    state = 'normal'
                    communication2 = line.invoice.reference
            ### end account_banking

            payment_obj.create(cr, uid,{
                'move_line_id': line.id,
                'amount_currency': line.amount_to_pay,
                'bank_id': line2bank.get(line.id),
                'order_id': payment.id,
                'partner_id': line.partner_id and line.partner_id.id or False,
                ### account banking
                # 'communication': line.ref or '/'
                'communication': communication,
                'communication2': communication2,
                'state': state,
                ### end account banking
                'date': date_to_pay,
                'currency': line.invoice and line.invoice.currency_id.id or False,
                }, context=context)
        return {'type': 'ir.actions.act_window_close'}

payment_order_create()
