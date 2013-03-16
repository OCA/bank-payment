# -*- encoding: utf-8 -*-
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

'''
This module contains a single "wizard" for including a 'sent' state for manual
bank transfers.
'''

import wizard
import pooler


class payment_manual(osv.Model):
    _name = 'payment.manual'
    _description = 'Set payment orders to \'sent\' manually'

    def default_get(self, cr, uid, fields_list, context=None):
        if context and context.get('active_ids'):
            payment_order_obj = self.pool.get('payment.order')
            for res_id in context['active_ids']:
                payment_order_obj.action_sent(
                    cr, uid, [res_id], context=context)
        return super(payment_manual, self).default_get(
            cr, uid, fields_list, context=None)
