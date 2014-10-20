# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module (C) 2011 - 2013 Therp BV (<http://therp.nl>).
#                (C) 2011 Smile Benelux (<http://smile.fr>).
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

from operator import itemgetter
from openerp.osv import fields, orm


class account_move_line(orm.Model):
    _inherit = "account.move.line"

    def amount_to_receive(self, cr, uid, ids, name, arg=None, context=None):
        """
        Return the amount still to receive regarding all the debit orders
        (excepting canceled orders).
        This is the reverse from amount_to_pay() in
        account_payment/account_move_line.py
        """
        if arg is None:
            arg = {}
        if not ids:
            return {}
        cr.execute("""SELECT ml.id,
                    CASE WHEN ml.amount_currency > 0
                        THEN ml.amount_currency
                        ELSE ml.debit
                    END -
                    (SELECT coalesce(sum(amount_currency),0)
                        FROM payment_line pl
                            INNER JOIN payment_order po
                                ON (pl.order_id = po.id)
                        WHERE move_line_id = ml.id
                        AND pl.storno is false
                        AND po.state != 'cancel') AS amount
                    FROM account_move_line ml
                    WHERE id IN %s""", (tuple(ids), ))
        r = dict(cr.fetchall())
        return r

    def _to_receive_search(self, cr, uid, obj, name, args, context=None):
        """
        Reverse of account_payment/account_move_line.py:_to_pay_search()
        """
        if not args:
            return []
        line_obj = self.pool.get('account.move.line')
        query = line_obj._query_get(cr, uid, context=context)
        where = ' and '.join(map(lambda x: '''(SELECT
        CASE WHEN l.amount_currency > 0
            THEN l.amount_currency
            ELSE l.debit
        END - coalesce(sum(pl.amount_currency), 0)
        FROM payment_line pl
        INNER JOIN payment_order po ON (pl.order_id = po.id)
        WHERE move_line_id = l.id
        AND pl.storno is false
        AND po.state != 'cancel'
        ) %(operator)s %%s ''' % {'operator': x[1]}, args))
        sql_args = tuple(map(itemgetter(2), args))

        cr.execute(('''SELECT id
            FROM account_move_line l
            WHERE account_id IN (select id
                FROM account_account
                WHERE type=%s AND active)
            AND reconcile_id IS null
            AND debit > 0
            AND ''' + where + ' and ' + query), ('receivable', ) + sql_args)

        res = cr.fetchall()
        if not res:
            return [('id', '=', '0')]
        return [('id', 'in', map(lambda x: x[0], res))]

    def line2bank(self, cr, uid, ids, payment_mode_id, context=None):
        '''I have to inherit this function for direct debits to fix the
        following issue : if the customer invoice has a value for
        'partner_bank_id', then it will take this partner_bank_id
        in the payment line... but, on a customer invoice,
        the partner_bank_id is the bank account of the company,
        not the bank account of the customer !
        '''
        if context is None:
            context = {}
        pay_mode_obj = self.pool['payment.mode']
        if payment_mode_id:
            pay_mode = pay_mode_obj.browse(
                cr, uid, payment_mode_id, context=context)
            if pay_mode.type.payment_order_type == 'debit':
                line2bank = {}
                bank_type = pay_mode_obj.suitable_bank_types(
                    cr, uid, payment_mode_id, context=context)
                for line in self.browse(cr, uid, ids, context=context):
                    line2bank[line.id] = False
                    if line.partner_id:
                        for bank in line.partner_id.bank_ids:
                            if bank.state in bank_type:
                                line2bank[line.id] = bank.id
                                break
                return line2bank
        return super(account_move_line, self).line2bank(
            cr, uid, ids, payment_mode_id, context=context)

    _columns = {
        'amount_to_receive': fields.function(
            amount_to_receive, method=True,
            type='float', string='Amount to receive',
            fnct_search=_to_receive_search),
    }
