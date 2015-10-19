# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Payment Partner module for Odoo
#    Copyright (C) 2014-2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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

from openerp import models, fields, api


class PaymentOrderCreate(models.TransientModel):
    _inherit = 'payment.order.create'

    payment_mode = fields.Selection([
        ('same', 'Same'),
        ('same_or_null', 'Same or empty'),
        ('any', 'Any'),
        ], string='Payment Mode on Invoice')

    @api.model
    def default_get(self, field_list):
        res = super(PaymentOrderCreate, self).default_get(field_list)
        context = self.env.context
        assert context.get('active_model') == 'payment.order',\
            'active_model should be payment.order'
        assert context.get('active_id'), 'Missing active_id in context !'
        pay_order = self.env['payment.order'].browse(context['active_id'])
        res['payment_mode'] = pay_order.mode.default_payment_mode
        return res

    @api.multi
    def extend_payment_order_domain(self, payment_order, domain):
        res = super(PaymentOrderCreate, self).extend_payment_order_domain(
            payment_order, domain)
        if self.invoice and self.payment_mode:
            if self.payment_mode == 'same':
                domain.append(
                    ('invoice.payment_mode_id', '=', payment_order.mode.id))
            elif self.payment_mode == 'same_or_null':
                domain += [
                    '|',
                    ('invoice.payment_mode_id', '=', False),
                    ('invoice.payment_mode_id', '=', payment_order.mode.id)]
            # if payment_mode == 'any', don't modify domain
        return res
