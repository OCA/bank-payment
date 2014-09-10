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

"""This module contains a single "wizard" for confirming manual
bank transfers.
"""

from openerp import models, fields, api
from openerp import netsvc


class PaymentManual(models.TransientModel):
    _name = 'payment.manual'
    _description = 'Send payment order(s) manually'

    payment_order_ids = fields.Many2many(
        comodel_name='payment.order', relation='wiz_manual_payorders_rel',
        column1='wizard_id', column2='payment_order_id',
        string='Payment orders', readonly=True),

    def create(self, vals):
        payment_order_ids = self.env.context.get('active_ids', [])
        vals['payment_order_ids'] = [[6, 0, payment_order_ids]]
        return super(PaymentManual, self).create(vals)

    @api.one
    def button_ok(self):
        wf_service = netsvc.LocalService('workflow')
        for order_id in self.payment_order_ids:
            wf_service.trg_validate(self.env.uid, 'payment.order', order_id.id,
                                    'done', self.env.cr)
        return {'type': 'ir.actions.act_window_close'}
