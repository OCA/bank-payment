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
This module contains a single "wizard" for confirming manual
bank transfers.
'''

from openerp.osv import orm, fields
from openerp import netsvc


class payment_manual(orm.TransientModel):
    _name = 'payment.manual'
    _description = 'Send payment order(s) manually'

    _columns = {
        'payment_order_ids': fields.many2many(
            'payment.order',
            'wiz_manual_payorders_rel',
            'wizard_id',
            'payment_order_id',
            'Payment orders',
            readonly=True
        ),
    }

    def create(self, cr, uid, vals, context=None):
        payment_order_ids = context.get('active_ids', [])
        vals.update({
            'payment_order_ids': [[6, 0, payment_order_ids]],
        })
        return super(payment_manual, self).create(
            cr, uid, vals, context=context
        )

    def button_ok(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService('workflow')
        for wiz in self.browse(cr, uid, ids, context=context):
            for order_id in wiz.payment_order_ids:
                wf_service.trg_validate(
                    uid, 'payment.order', order_id.id, 'done', cr)
        return {'type': 'ir.actions.act_window_close'}
