# -*- coding: utf-8 -*-
from osv import osv, fields

class payment_order(osv.osv):
    _inherit = 'payment.order'

    def fields_view_get(self, cr, user, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        """ 
        Pretty awful workaround for no dynamic domain possible on 
        widget='selection'

        The domain is encoded in the context

        Uhmm, are these results are cached?
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
                    cr, user, args=domain)
                # also update the domain
                res['fields']['mode']['domain'] = domain
        return res
payment_order()

class payment_order_create(osv.osv_memory):
    _inherit = 'payment.order.create'
    
    def search_entries(self, cr, uid, ids, context=None):
        """
        This method taken from account_payment module.
        We adapt the domain based on the payment_order_type
        """
        line_obj = self.pool.get('account.move.line')
        mod_obj = self.pool.get('ir.model.data')
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        search_due_date = data['duedate']
        
        ### start account_direct_debit ###
        payment = self.pool.get('payment.order').browse(cr, uid, context['active_id'], context=context)
        # Search for move line to pay:
        if payment.payment_order_type == 'debit':
            domain = [('reconcile_id', '=', False), ('account_id.type', '=', 'receivable'), ('amount_to_receive', '>', 0)]
        else:
            domain = [('reconcile_id', '=', False), ('account_id.type', '=', 'payable'), ('amount_to_pay', '>', 0)]
        # domain = [('reconcile_id', '=', False), ('account_id.type', '=', 'payable'), ('amount_to_pay', '>', 0)]
        ### end account_direct_debit ###

        domain = domain + ['|', ('date_maturity', '<=', search_due_date), ('date_maturity', '=', False)]
        line_ids = line_obj.search(cr, uid, domain, context=context)
        context.update({'line_ids': line_ids})
        model_data_ids = mod_obj.search(cr, uid,[('model', '=', 'ir.ui.view'), ('name', '=', 'view_create_payment_order_lines')], context=context)
        resource_id = mod_obj.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']
        return {'name': ('Entrie Lines'),
                'context': context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'payment.order.create',
                'views': [(resource_id,'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
        }
payment_order_create()
