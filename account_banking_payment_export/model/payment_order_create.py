# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 ACSONE SA/NV (<http://acsone.eu>);.
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


class payment_order_create(orm.TransientModel):
    _inherit = 'payment.order.create'

    def create_payment(self, cr, uid, ids, context=None):
        '''This method adapts the core create_payment() 
        to pass the payment mode to line2bank() through the context,
        so it is in turn propagated to suitable_bank_types().
        
        This is necessary because the core does not propagate the payment mode to line2bank: t = None in
        http://bazaar.launchpad.net/~openerp/openobject-addons/7.0/view/head:/account_payment/wizard/account_payment_order.py#L72
        
        Hack idea courtesy Stefan Rijnhart.
        '''
        if context is None:
            context = {}
        order_obj = self.pool.get('payment.order')
        payment = order_obj.browse(cr, uid, context['active_id'], context=context)
        context['_fix_payment_mode_id'] = payment.mode.id
        return super(payment_order_create, self).create_payment(cr, uid, ids, context=context)
    

class account_move_line(orm.Model):
    _inherit = 'account.move.line'
    
    def line2bank(self, cr, uid, ids, payment_mode_id=None, context=None):
        '''Obtain payment_type from context, see create_payment above'''
        if context is None:
            context = {}
        payment_mode_id = payment_mode_id or context.get('_fix_payment_mode_id')
        return super(account_move_line, self).line2bank(cr, uid, ids, payment_mode_id, context=context)

