# -*- coding: utf-8 -*-
from osv import osv, fields

class payment_order_create(osv.osv_memory):

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
        res = super(payment_order_create, self).default_get(
            cr, uid, fields_list, context=context)

        if (fields_list and 'entries' in fields_list
            and 'entries' not in res
            and context and context.get('line_ids', False)
            ):
            res['entries'] = context['line_ids']

        return res

payment_order_create()
