# -*- coding: utf-8 -*-
from openerp.osv import orm, fields
import netsvc
from tools.translate import _

class payment_order(orm.Model):
    _inherit = 'payment.order'

    def fields_view_get(self, cr, user, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        """ 
        We use the same form for payment and debit orders, but they
        are accessible through different menu items. The user should only
        be allowed to select a payment mode that applies to the type of order
        i.e. payment or debit.

        A pretty awful workaround is needed for the fact that no dynamic
        domain is possible on the selection widget. This domain is encoded
        in the context of the menu item.
        """
        if not context:
            context = {}
        res = super(payment_order, self).fields_view_get(
            cr, user, view_id, view_type, context, toolbar, submenu)
        if context.get('search_payment_order_type', False) and view_type == 'form':
            if 'mode' in res['fields'] and 'selection' in res['fields']['mode']:
                mode_obj = self.pool.get('payment.mode')
                domain = ['|', ('type', '=', False), ('type.payment_order_type', '=',  
                           context['search_payment_order_type'])]
                # the magic is in the value of the selection
                res['fields']['mode']['selection'] = mode_obj._name_search(
                    cr, user, args=domain, context=context)
                # also update the domain
                res['fields']['mode']['domain'] = domain
        return res

    def test_undo_done(self, cr, uid, ids, context=None):
        """ 
        Called from the workflow. Used to unset done state on
        payment orders that were reconciled with bank transfers
        which are being cancelled 
        """
        for order in self.browse(cr, uid, ids, context=context):
            if order.payment_order_type == 'debit':
                for line in order.line_ids:
                    if line.storno:
                        return False
        return super(payment_order, self).test_undo_done(
            cr, uid, ids, context=context)
