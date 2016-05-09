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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class banking_transaction_wizard(orm.TransientModel):
    _inherit = 'banking.transaction.wizard'

    def write(self, cr, uid, ids, vals, context=None):
        """
        Check for manual payment orders or lines
        """
        if not vals or not ids:
            return True
        manual_payment_order_id = vals.pop('manual_payment_order_id', False)
        manual_payment_line_id = vals.pop('manual_payment_line_id', False)
        res = super(banking_transaction_wizard, self).write(
            cr, uid, ids, vals, context=context)
        if manual_payment_order_id or manual_payment_line_id:
            transaction_id = self.browse(
                cr, uid, ids[0],
                context=context).import_transaction_id
            write_vals = {}
            if manual_payment_order_id:
                payment_order = self.pool.get('payment.order').browse(
                    cr, uid, manual_payment_order_id,
                    context=context)
                if payment_order.payment_order_type == 'payment':
                    sign = 1
                else:
                    sign = -1
                total = (payment_order.total + sign *
                         transaction_id.statement_line_id.amount)
                if not self.pool.get('res.currency').is_zero(
                        cr, uid,
                        transaction_id.statement_line_id.statement_id.currency,
                        total):
                    raise orm.except_orm(
                        _('Error'),
                        _('When matching a payment order, the amounts have to '
                          'match exactly'))

                if (payment_order.mode and
                        payment_order.mode.transfer_account_id):
                    transaction_id.statement_line_id.write({
                        'account_id': (
                            payment_order.mode.transfer_account_id.id),
                    })
                write_vals.update(
                    {'payment_order_id': manual_payment_order_id,
                     'match_type': 'payment_order_manual'})
            else:
                write_vals.update(
                    {'payment_line_id': manual_payment_line_id,
                     'match_type': 'payment_manual'})
            self.pool.get('banking.import.transaction').clear_and_write(
                cr, uid, transaction_id.id, write_vals, context=context)
        return res

    _columns = {
        'payment_line_id': fields.related(
            'import_transaction_id',
            'payment_line_id',
            string="Matching payment or storno",
            type='many2one',
            relation='payment.line',
            readonly=True,
        ),
        'payment_order_ids': fields.related(
            'import_transaction_id',
            'payment_order_ids',
            string="Matching payment orders",
            type='many2many',
            relation='payment.order',
        ),
        'payment_order_id': fields.related(
            'import_transaction_id',
            'payment_order_id',
            string="Payment order to reconcile",
            type='many2one',
            relation='payment.order',
        ),
        'manual_payment_order_id': fields.many2one(
            'payment.order',
            'Match this payment order',
            domain=[
                ('state', '=', 'sent'),
            ],
        ),
        'manual_payment_line_id': fields.many2one(
            'payment.line',
            'Match this payment line',
            domain=[
                ('order_id.state', '=', 'sent'),
                ('date_done', '=', False),
            ],
        ),
    }
