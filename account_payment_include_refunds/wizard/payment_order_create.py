# -*- coding: utf-8 -*-
#
##############################################################################
#
#     Authors: David Diz
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

class PaymentOrderCreate(models.TransientModel):
    _inherit = 'payment.order.create'            
            
    @api.multi
    def extend_payment_order_domain(self, payment_order, domain):
        super(PaymentOrderCreate, self).extend_payment_order_domain(
            payment_order, domain)
        if payment_order.payment_order_type == 'payment':
            # For orders of type 'payment' propose not only the credit lines,
            # propose too the refunds from the suppliers,
            # the sense of adding this refund invoices is to take care of them
            # and not to pay invoices from the same supplier with out decreasing
            # the amount of the refund
            location = domain.index(('credit', '>', 0))
            del domain[location]
            domain += [
                '|',
                ('credit', '>', 0),'&',
                ('debit', '>', 0),'&',
                ('account_id.type', '=', 'payable'),
                ('journal_id.type', '=', 'purchase_refund')
            ]
        return True
