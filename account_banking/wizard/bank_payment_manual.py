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

class payment_manual(wizard.interface):
    def _action_set_state_sent(self, cursor, uid, data, context):
        '''
        Set the payment order in state 'sent' to reflect money in transfer.
        '''
        payment_order_obj = pooler.get_pool(cursor.dbname)\
                .get('payment.order')
        payment_order_obj.action_sent(cursor, uid, [data['id']], context)
        return {}
        
    states= {
        'init' : {
            'actions': [],
            'result': {
                'type':'action',
                'action': _action_set_state_sent,
                'state': 'end'
            }
        }
    }

payment_manual('account_banking.payment_manual')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
