# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Therp BV (<http://therp.nl>).
#
#    All other contributions are (C) by their respective contributors
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

from openerp import models, api
from lxml import etree


class PaymentOrderCreate(models.TransientModel):
    _inherit = 'payment.order.create'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """Modify view to accomodate fields to direct debit orders."""
        res = super(PaymentOrderCreate, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        payment_order = self.env['payment.order'].browse(
            self.env.context['active_id'])
        if payment_order.payment_order_type == 'debit' and view_type == 'form':
            eview = etree.fromstring(res['arch'])
            partners_fields = eview.xpath("//field[@name='partners']")
            if partners_fields:
                partners_fields[0].set(
                    'domain', "[('customer', '=', True)]")
            accounts_fields = eview.xpath("//field[@name='accounts']")
            if accounts_fields:
                accounts_fields[0].set(
                    'domain', "[('type', '=', 'receivable')]")
            res['arch'] = etree.tostring(eview)
        return res

    @api.multi
    def extend_payment_order_domain(self, payment_order, domain):
        super(PaymentOrderCreate, self).extend_payment_order_domain(
            payment_order, domain)
        if payment_order.payment_order_type == 'debit':
            domain += ['|',
                       ('invoice', '=', False),
                       ('invoice.state', '!=', 'debit_denied'),
                       ('account_id.type', '=', 'receivable'),
                       ('amount_to_receive', '>', 0)]
        return True
