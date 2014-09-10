# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2014 OpenERP S.A. (http://www.openerp.com/)
#              (C) 2014 Akretion (http://www.akretion.com/)
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
from operator import itemgetter


# All the code below aims at fixing one small issue in _to_pay_search()
# But _to_pay_search() is the search function of the field 'amount_to_pay'
# which is a field.function and these functions are not inheritable in OpenERP.
# So we have to inherit the field 'amount_to_pay' and duplicate the related
# functions
# If the patch that I proposed in this bug report
# https://bugs.launchpad.net/openobject-addons/+bug/1275478
# is integrated in addons/account_payment, then we will be able to remove this
# file.         -- Alexis de Lattre
class account_move_line(orm.Model):
    _inherit = 'account.move.line'

    def amount_to_pay(self, cr, uid, ids, name, arg=None, context=None):
        """ Return the amount still to pay regarding all the payemnt orders
        (excepting cancelled orders)"""
        if not ids:
            return {}
        cr.execute("""SELECT ml.id,
                    CASE WHEN ml.amount_currency < 0
                        THEN - ml.amount_currency
                        ELSE ml.credit
                    END -
                    (SELECT coalesce(sum(amount_currency),0)
                        FROM payment_line pl
                            INNER JOIN payment_order po
                                ON (pl.order_id = po.id)
                        WHERE move_line_id = ml.id
                        AND po.state != 'cancel') AS amount
                    FROM account_move_line ml
                    WHERE id IN %s""", (tuple(ids),))
        r = dict(cr.fetchall())
        return r

    def _to_pay_search(self, cr, uid, obj, name, args, context=None):
        if not args:
            return []
        line_obj = self.pool.get('account.move.line')
        query = line_obj._query_get(cr, uid, context={})
        where = ' and '.join(map(lambda x: '''(SELECT
        CASE WHEN l.amount_currency < 0
            THEN - l.amount_currency
            ELSE l.credit
        END - coalesce(sum(pl.amount_currency), 0)
        FROM payment_line pl
        INNER JOIN payment_order po ON (pl.order_id = po.id)
        WHERE move_line_id = l.id
        AND po.state != 'cancel'
        ) %(operator)s %%s ''' % {'operator': x[1]}, args))
        sql_args = tuple(map(itemgetter(2), args))

        cr.execute(
            ('''\
            SELECT id
            FROM account_move_line l
            WHERE account_id IN (select id
                FROM account_account
                WHERE type in %s AND active)
            AND reconcile_id IS null
            AND credit > 0
            AND ''' + where + ' and ' + query
             ), (('payable', 'receivable'), ) + sql_args
        )
        # The patch we have compared to the original function in
        # addons/account_payment is just above :
        # original code : type = 'payable'
        # fixed code :    type in ('payable', 'receivable')

        res = cr.fetchall()
        if not res:
            return [('id', '=', '0')]
        return [('id', 'in', map(lambda x:x[0], res))]

    _columns = {
        'amount_to_pay': fields.function(
            amount_to_pay,
            type='float',
            string='Amount to pay',
            fnct_search=_to_pay_search
        ),
    }
