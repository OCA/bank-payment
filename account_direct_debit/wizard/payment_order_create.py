# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Therp BV (<http://therp.nl>).
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

from openerp import models, api


class PaymentOrderCreate(models.TransientModel):
    _inherit = 'payment.order.create'

    @api.multi
    def extend_payment_order_domain(self, payment_order, domain):
        super(PaymentOrderCreate, self).extend_payment_order_domain(
            payment_order, domain)
        if payment_order.payment_order_type == 'debit':
            # Monkey patch for fixing problem with the core search function
            # when args has ('invoice', '=', False), referred in the issue #4857
            # (https://github.com/odoo/odoo/issues/4857)
            #
            # Original domain:
            # domain += ['|',
            #            ('invoice', '=', False),
            #            ('invoice.state', '!=', 'debit_denied'),
            #            ('account_id.type', '=', 'receivable'),
            #            ('amount_to_receive', '>', 0)]
            self.env.cr.execute(
                "SELECT l.id "
                "FROM account_move_line l "
                "LEFT OUTER JOIN account_invoice i "
                "ON l.move_id = i.move_id "
                "INNER JOIN account_account a "
                "ON a.id = l.account_id "
                "WHERE i.id IS NULL"
                "  AND l.reconcile_id IS NULL"
                "  AND a.type in ('receivable', 'payable')")
            ids = [x[0] for x in self.env.cr.fetchall()]
            domain += ['|',
                       ('id', 'in', ids),
                       ('invoice.state', '!=', 'debit_denied'),
                       ('account_id.type', '=', 'receivable'),
                       ('amount_to_receive', '>', 0)]
        return True
