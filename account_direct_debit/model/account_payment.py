# -*- coding: utf-8 -*-
import time
from osv import osv, fields
import netsvc
from tools.translate import _

class payment_mode(osv.osv):
    _inherit = 'payment.mode'
    _columns = {
        'transfer_account_id': fields.many2one(
            'account.account', 'Transfer account',
            domain=[('type', '=', 'other'),
                    ('reconcile', '=', True)],
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

    def debit_reconcile_transfer(self, cr, uid, payment_order_id, 
                        amount, log, context=None):
        """
        During import of bank statements, create the reconcile on the transfer
        account containing all the move lines on the transfer account.
        """
        move_line_obj = self.pool.get('account.move.line')

        def get_balance(line_ids):
            total = 0.0
            for line in move_line_obj.read(
                cr, uid, line_ids, ['debit', 'credit'], context=context):
                total += (line['debit'] or 0.0) - (line['credit'] or 0.0)
            return total

        def is_zero(move_line, total):
            return self.pool.get('res.currency').is_zero(
                cr, uid, move_line.company_id.currency_id, total)

        order = self.browse(cr, uid, payment_order_id, context)
        line_ids = []
        reconcile_id = False
        for order_line in order.line_ids:
            for line in order_line.debit_move_line_id.move_id.line_id:
                if line.account_id.type == 'other' and not line.reconcile_id:
                    line_ids.append(line.id)
        import pdb
        pdb.set_trace()
        if is_zero(order.line_ids[0].debit_move_line_id,
                   get_balance(line_ids) - amount):
            reconcile_id = self.pool.get('account.move.reconcile').create(
                cr, uid, 
                {'type': 'auto', 'line_id': [(6, 0, line_ids)]},
                context)
        return reconcile_id

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
                    'date': time.strftime('%Y-%m-%d'),
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
                
                # register the debit move line on the payment line
                # and call reconciliation on it
                payment_line_obj.write(
                    cr, uid, line.id,
                    {'debit_move_line_id': reconcile_move_line_id},
                    context=context)

                payment_line_obj.debit_reconcile(
                    cr, uid, line.id, context=context)
                account_move_obj.post(cr, uid, [move_id], context=context)
        return res

payment_order()

class payment_line(osv.osv):
    _inherit = 'payment.line'

    def debit_storno(self, cr, uid, payment_line_id, storno_move_line_id, context=None):
        """
        Process a payment line from a direct debit order which has
        been canceled by the bank or by the user:
        - Undo the reconciliation of the payment line with the move
        line that it originated from, and re-reconciliated with
        the credit payment in the bank journal of the same amount and
        on the same account.
        - Mark the payment line for being reversed.
        
        :param payment_line_id: the single id of the canceled payment line
        :param storno_move_line_id: the credit payment in the bank journal
        """

        if isinstance(payment_line_id, (list, tuple)):
            payment_line_id = payment_line_id[0]
        reconcile_obj = self.pool.get('account.move.reconcile')
        move_line_obj = self.pool.get('account.move.line')
        payment_line = self.browse(cr, uid, payment_line_id, context=context)

        debit_move_line = payment_line.debit_move_line_id
        if (not debit_move_line):
            raise osv.except_osv(
                _('Can not process storno'),
                _('No move line for line %s') % payment_line.name)
        if payment_line.storno:
            raise osv.except_osv(
                _('Can not process storno'),
                _('Cancelation of payment line \'%s\' has already been ' +
                  'processed') % payment_line.name)

        def is_zero(total):
            return self.pool.get('res.currency').is_zero(
                cr, uid, debit_move_line.company_id.currency_id, total)

        # check validity of the proposed move line
        torec_move_line = move_line_obj.browse(
            cr, uid, storno_move_line_id, context=context)
        if not (is_zero(torec_move_line.debit - debit_move_line.debit) and
                is_zero(torec_move_line.credit - debit_move_line.credit) and
                torec_move_line.account_id.id == debit_move_line.account_id.id):
            raise osv.except_osv(
                _('Can not process storno'),
                _('%s is not a drop-in replacement for %s') % (
                    torec_move_line.name, debit_move_line.name))
        if payment_line.storno:
            raise osv.except_osv(
                _('Can not process storno'),
                _('Debit order line %s has already been cancelled') % (
                    payment_line.name))

        # replace move line in reconciliation
        reconcile_id = False
        if (payment_line.move_line_id.reconcile_partial_id and 
            debit_move_line_id.id in
            payment_line.move_line_id.reconcile_partial_id.line_partial_ids):
            reconcile_id = payment_line.move_line_id.reconcile_partial_id
            vals = {
                'line_partial_ids': 
                [(3, debit_move_line_id.id), (4, torec_move_line.id)],
                }
        elif (payment_line.move_line_id.reconcile_id and 
              debit_move_line_id.id in
              payment_line.move_line_id.reconcile_id.line_id):
            reconcile_id = payment_line.move_line_id.reconcile_id
            vals = {
                'line_id':
                    [(3, debit_move_line_id.id), (4, torec_move_line.id)]
                }
        if not reconcile_id:
            raise osv.except_osv(
                _('Can not perform storno'),
                _('Debit order line %s does not occur in the list of '
                  'reconciliation move lines of its origin') % 
                debit_move_line_id.name)
        reconcile_obj.write(cr, uid, reconcile_id, vals, context=context)
        self.write(cr, uid, payment_line_id, {'storno': True}, context=context)
        #for line_id in line_ids:
        #    netsvc.LocalService("workflow").trg_trigger(
        #        uid, 'account.move.line', line_id, cr)

    def debit_reconcile(self, cr, uid, payment_line_id, context=None):
        """
        Reconcile a debit order's payment line with the the move line
        that it is based on.
        As the amount is derived directly from the counterpart move line,
        we do not expect a write off. Take partially reconcilions into
        account though.

        :param payment_line_id: the single id of the canceled payment line
        """

        if isinstance(payment_line_id, (list, tuple)):
            payment_line_id = payment_line_id[0]
        reconcile_obj = self.pool.get('account.move.reconcile')
        move_line_obj = self.pool.get('account.move.line')
        payment_line = self.browse(cr, uid, payment_line_id, context=context)

        debit_move_line = payment_line.debit_move_line_id
        torec_move_line = payment_line.move_line_id

        if payment_line.storno:
            raise osv.except_osv(
                _('Can not reconcile'),
                _('Cancelation of payment line \'%s\' has already been ' +
                  'processed') % payment_line.name)
        if (not debit_move_line or not torec_move_line):
            raise osv.except_osv(
                _('Can not reconcile'),
                _('No move line for line %s') % payment_line.name)     
        if torec_move_line.reconcile_id or torec_move_line.reconcile_partial_id:
            raise osv.except_osv(
                _('Error'),
                _('Move line %s has already been reconciled') % 
                torec_move_line.name
                )
        if torec_move_line.reconcile_id or torec_move_line.reconcile_partial_id:
            raise osv.except_osv(
                _('Error'),
                _('Move line %s has already been reconciled') % 
                torec_move_line.name
                )
        
        def get_balance(line_ids):
            total = 0.0
            for line in move_line_obj.read(
                cr, uid, line_ids, ['debit', 'credit'], context=context):
                total += (line['debit'] or 0.0) - (line['credit'] or 0.0)
            return total

        def is_zero(total):
            return self.pool.get('res.currency').is_zero(
                cr, uid, debit_move_line.company_id.currency_id, total)

        line_ids = [debit_move_line.id, torec_move_line.id]
        if debit_move_line.reconcile_partial_id:
            line_ids = [
                x.id for x in debit_move_line.reconcile_partial_id.line_partial_ids] + [torec_move_line_id]

        total = get_balance(line_ids)
        vals = {
            'type': 'auto',
            'line_id': is_zero(total) and [(6, 0, line_ids)] or [(6, 0, [])],
            'line_partial_ids': is_zero(total) and [(6, 0, [])] or [(6, 0, line_ids)],
            }
        if debit_move_line.reconcile_partial_id:
            reconcile_obj.write(
                cr, uid, debit_move_line.reconcile_partial_id.id,
                vals, context=context)
        else:
            reconcile_obj.create(
                cr, uid, vals, context=context)
        for line_id in line_ids:
            netsvc.LocalService("workflow").trg_trigger(
                uid, 'account.move.line', line_id, cr)

    _columns = {
        'debit_move_line_id': fields.many2one(
            # this line is part of the credit side of move 2a 
            # from the documentation
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


                  
