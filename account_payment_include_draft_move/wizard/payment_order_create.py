# -*- coding: utf-8 -*-
#
##############################################################################
#
#     Authors: Adrien Peiffer
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
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

POSTED_MOVE_DOMAIN = ('move_id.state', '=', 'posted')


class PaymentOrderCreate(models.TransientModel):
    _inherit = 'payment.order.create'

    @api.multi
    def extend_payment_order_domain(self, payment_order, domain):
        if POSTED_MOVE_DOMAIN in domain:
            pos = domain.index(POSTED_MOVE_DOMAIN)
            domain[pos] = (1, '=', 1)
        return super(PaymentOrderCreate, self)\
            .extend_payment_order_domain(payment_order, domain)
