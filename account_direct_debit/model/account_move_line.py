# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    This module additional (C) 2011 Therp BV (<http://therp.nl>).
#                           (C) 2011 Smile Benelux (<http://smile.fr>).
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
from osv import fields, osv
from tools.translate import _

class account_move_line(osv.osv):
    _inherit = "account.move.line"

    def amount_to_receive(self, cr, uid, ids, name, arg={}, context=None):
        """ 
        Return the amount still to receive regarding all the debit orders
        (excepting canceled orders).
        This is the reverse from amount_to_pay() in
        account_payment/account_move_line.py
        """
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
                    WHERE id IN %s""", (tuple(ids),))
        r = dict(cr.fetchall())
        return r

    def _to_receive_search(self, cr, uid, obj, name, args, context=None):
        if not args:
            return []
        line_obj = self.pool.get('account.move.line')
        query = line_obj._query_get(cr, uid, context={})
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
            AND ''' + where + ' and ' + query), ('receivable',)+sql_args )

        res = cr.fetchall()
        if not res:
            return [('id', '=', '0')]
        return [('id', 'in', map(lambda x:x[0], res))]

    def _dummy(self, cr, user, ids, name, arg, context=None):
        res = {}
        if ids:
            res = dict([(x, False) for x in ids])
        return res

    def _invoice_payment_term_id_search(
        self, cr, uid, obj, name, args, context=None):
        """
        Allow to search move lines associated with an invoice with
        a particular payment term
        """
        if not args:
            return []
        invoice_obj = self.pool.get('account.invoice')
        invoice_ids = invoice_obj.search(
            cr, uid, [('payment_term', args[0][1], args[0][2])],
            context=context)
        operator = 'in' # (args[0][1] not in ['in', '=', '==', 'like', 'ilike']
                        # and 'not in' or 'in')
        if not invoice_ids:
            return [('id', operator, [])]
        cr.execute('SELECT l.id ' \
                'FROM account_move_line l, account_invoice i ' \
                'WHERE l.move_id = i.move_id AND i.id in %s', (tuple(invoice_ids),))
        res = cr.fetchall()
        if not res:
            return [('id', '=', False)]
        return [('id', operator, [x[0] for x in res])]

    def _invoice_state_search(self, cr, uid, obj, name, args, context=None):
        if not args:
            return []
        invoice_obj = self.pool.get('account.invoice')
        invoice_ids = invoice_obj.search(
            cr, uid, [('state', args[0][1], args[0][2])],
            context=context)
        operator = 'in' # (args[0][1] not in ['in', '=', '==', 'like', 'ilike']
                        # and 'not in' or 'in')
        if not invoice_ids:
            return [('id', operator, [])]
        cr.execute('SELECT l.id ' \
                'FROM account_move_line l, account_invoice i ' \
                'WHERE l.move_id = i.move_id AND i.id in %s', (tuple(invoice_ids),))
        res = cr.fetchall()
        if not res:
            return [('id', '=', False)]
        return [('id', operator, [x[0] for x in res])]
        
    _columns = {
        'amount_to_receive': fields.function(
            amount_to_receive, method=True,
            type='float', string='Amount to receive',
            fnct_search=_to_receive_search),
        'payment_term_id': fields.function(
            _dummy, method=True,
            string='Select by invoice payment term',
            type='many2one', relation='account.payment.term',
            fnct_search=_invoice_payment_term_id_search),
        'invoice_state': fields.function(
            _dummy, method=True,
            string='Select by invoice state',
            type='char', size=24,
            fnct_search=_invoice_state_search),
        }

account_move_line()
