# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#              (C) 2011 - 2013 Therp BV (<http://therp.nl>).
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

'''
This module contains a single "wizard" for including a 'sent' state for manual
bank transfers.
'''

from openerp.osv import orm, fields
from openerp import netsvc


class payment_manual(orm.TransientModel):
    _name = 'payment.manual'
    _description = 'Set payment orders to \'sent\' manually'

    def default_get(self, cr, uid, fields_list, context=None):
        if context and context.get('active_ids'):
            payment_order_obj = self.pool.get('payment.order')
            wf_service = netsvc.LocalService('workflow')
            for order_id in context['active_ids']:
                wf_service.trg_validate(
                    uid, 'payment.order', order_id, 'sent', cr)
        return super(payment_manual, self).default_get(
            cr, uid, fields_list, context=None)

    _columns = {
        # dummy field, to trigger a call to default_get
        'name': fields.char('Name', size=1),
        }

