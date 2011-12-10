# -*- coding: utf-8 -*-
from osv import osv, fields
import netsvc
from tools.translate import _

class payment_mode(osv.osv):
    _inherit = 'payment.mode'
    _columns = {
        'transfer_account_id': fields.many2one(
            'account.account', 'Transfer account',
            domain=[('type', '=', 'other')],
            help=('Pay off lines in sent orders with a ' +
                  'move on this account. For debit type modes only'),
            ),
        'transfer_journal_id': fields.many2one(
            'account.journal', 'Transfer journal',
            help=('Journal to write payment entries when confirming ' +
                  'a debit order of this mode'),
            ),
        }
payment_mode()

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

    def _reconcile_debit_order_move_line(self, cr, uid, origin_move_line_id,
                  transfer_move_line_id, context=None):
        """
        Reconcile the debit order's move lines at generation time.
        As the amount is derived directly from the counterpart move line,
        we do not expect a write off. Take partially reconcilions into
        account though.
        """
        reconcile_obj = self.pool.get('account.move.reconcile')
        move_line_obj = self.pool.get('account.move.line')
        line_ids = [origin_move_line_id, transfer_move_line_id]
        (origin, transfer) = move_line_obj.browse(
            cr, uid, line_ids, context=context)
        if origin.reconcile_partial_id:
            line_ids = [x.id for x in
                   origin.reconcile_partial_id.line_partial_ids + [transfer]
                   ]

        total = 0.0
        company_currency_id = origin.company_id.currency_id
        for line in move_line_obj.read(
            cr, uid, line_ids, ['debit', 'credit'], context=context):
            total += (line['debit'] or 0.0) - (line['credit'] or 0.0)
        full = self.pool.get('res.currency').is_zero(
            cr, uid, company_currency_id, total)
        vals = {
            'type': 'auto',
            'line_id': full and [(6, 0, line_ids)] or [(6, 0, [])],
            'line_partial_ids': full and [(6, 0, [])] or [(6, 0, line_ids)],
            }
        if origin.reconcile_partial_id:
            reconcile_obj.write(
                cr, uid, origin.reconcile_partial_id.id,
                vals, context=context)
        else:
            reconcile_obj.create(
                cr, uid, vals, context=context)
        for line_id in line_ids:
            netsvc.LocalService("workflow").trg_trigger(
                uid, 'account.move.line', line_id, cr)

    def action_sent(self, cr, uid, ids, context=None):
        """ 
        Create the moves that pay off the move lines from
        the debit order. This happens when the debit order file is
        generated.
        """
        res = super(payment_order, self).action_sent(
            cr, uid, ids, context)

        account_move_obj = self.pool.get('account.move')
        account_move_line_obj = self.pool.get('account.move.line')
        payment_line_obj = self.pool.get('payment.line')
        for order in self.browse(cr, uid, ids, context=context):
            if order.payment_order_type != 'debit':
                continue
            for line in order.line_ids:
                # basic checks
                if not line.move_line_id:
                    raise osv.except_osv(
                        _('Error'),
                        _('No move line provided for line %s') % line.name)
                if line.move_line_id.reconcile_id:
                    raise osv.except_osv(
                        _('Error'),
                        _('Move line %s has already been paid/reconciled') % 
                        line.move_line_id.name
                        )

                move_id = account_move_obj.create(cr, uid, {
                        'journal_id': order.mode.transfer_journal_id.id,
                        'name': 'Debit order %s' % line.move_line_id.move_id.name,
                        'reference': 'DEB%s' % line.move_line_id.move_id.name,
                        }, context=context)

                # TODO: multicurrency
                
                # create the debit move line on the transfer account
                vals = {
                    'name': 'Debit order for %s' % (
                        line.move_line_id.invoice and 
                        line.move_line_id.invoice.number or 
                        line.move_line_id.name),
                    'move_id': move_id,
                    'partner_id': line.partner_id.id,
                    'account_id': order.mode.transfer_account_id.id,
                    'credit': 0.0,
                    'debit': line.amount,
                    }
                transfer_move_line_id = account_move_line_obj.create(
                    cr, uid, vals, context=context)

                # create the debit move line on the receivable account
                vals.update({
                        'account_id': line.move_line_id.account_id.id,
                        'credit': line.amount,
                        'debit': 0.0,
                        })               
                reconcile_move_line_id = account_move_line_obj.create(
                    cr, uid, vals, context=context)

                payment_line_obj.write(
                    cr, uid, line.id,
                    {'debit_move_line_id': reconcile_move_line_id},
                    context=context)

                account_move_obj.post(cr, uid, [move_id], context=context)
                self._reconcile_debit_order_move_line(
                    cr, uid, line.move_line_id.id, reconcile_move_line_id,
                    context=context)
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

class payment_line(osv.osv):
    _inherit = 'payment.line'
    _columns = {
        'debit_move_line_id': fields.many2one(
            'account.move.line', 'Debit move line',
            readonly=True,
            help="Move line through which the debit order pays the invoice"),
        'storno': fields.boolean(
            'Storno',
            readonly=True,
            help=("If this is true, the debit order has been canceled " +
                  "by the bank or by the customer")),
        }
payment_line()

                  
