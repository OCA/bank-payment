# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 - 2013 Therp BV (<http://therp.nl>).
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

from openerp.osv import orm


class payment_order_create(orm.TransientModel):
    _inherit = 'payment.order.create'

    def default_get(self, cr, uid, fields_list, context=None):
        """
        Automatically add the candidate move lines to
        the payment order, instead of only applying them
        to the domain.

        We make use of the fact that the search_entries
        method passes an action without a res_id so that a
        new instance is created. Inject the line_ids, which have
        been placed in the context at object
        creation time.
        """
        if context is None:
            context = {}
        res = super(payment_order_create, self).default_get(
            cr, uid, fields_list, context=context)

        if (fields_list and
                'entries' in fields_list and
                'entries' not in res and
                context.get('line_ids', False)):
            res['entries'] = context['line_ids']

        return res
