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
                  'move on this account. For debit type modes only. ' +
                  'You can only select accounts of type regular that ' +
                  'are marked for reconciliation'),
            ),
        'transfer_journal_id': fields.many2one(
            'account.journal', 'Transfer journal',
            help=('Journal to write payment entries when confirming ' +
                  'a debit order of this mode'),
            ),
        'payment_term_ids': fields.many2many(
            'account.payment.term', 'account_payment_order_terms_rel', 
            'mode_id', 'term_id', 'Payment terms',
            help=('Limit selected invoices to invoices with these payment ' +
                  'terms')
            ),
        }
payment_mode()

class payment_order(osv.osv):
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
                    cr, user, args=domain)
                # also update the domain
                res['fields']['mode']['domain'] = domain
        return res

    def debit_reconcile_transfer(self, cr, uid, payment_order_id, 
                                 amount, currency, context=None):
        """
        During import of bank statements, create the reconcile on the transfer
        account containing all the open move lines on the transfer account.
        """
        move_line_obj = self.pool.get('account.move.line')
        order = self.browse(cr, uid, payment_order_id, context)
        line_ids = []
        reconcile_id = False
        for order_line in order.line_ids:
            for line in order_line.debit_move_line_id.move_id.line_id:
                if line.account_id.type == 'other' and not line.reconcile_id:
                    line_ids.append(line.id)
        if self.pool.get('res.currency').is_zero(
            cr, uid, currency,
            move_line_obj.get_balance(cr, uid, line_ids) - amount):
            reconcile_id = self.pool.get('account.move.reconcile').create(
                cr, uid, 
                {'type': 'auto', 'line_id': [(6, 0, line_ids)]},
                context)
            # set direct debit order to finished state
            wf_service = netsvc.LocalService('workflow')
            wf_service.trg_validate(
                uid, 'payment.order', payment_order_id, 'done', cr)
        return reconcile_id

    def debit_unreconcile_transfer(self, cr, uid, payment_order_id, reconcile_id,
                                 amount, currency, context=None):
        """
        Due to a cancelled bank statements import, unreconcile the move on
        the transfer account. Delegate the conditions to the workflow.
        Raise on failure for rollback.
        """
        self.pool.get('account.move.reconcile').unlink(
            cr, uid, reconcile_id, context=context)
        wkf_ok = netsvc.LocalService('workflow').trg_validate(
            uid, 'payment.order', payment_order_id, 'undo_done', cr)
        if not wkf_ok:
            raise osv.except_osv(
                _("Cannot unreconcile"),
                _("Cannot unreconcile debit order: "+
                  "Workflow will not allow it."))
        return True

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
            else:
                # TODO: define conditions for 'payment' orders
                return False
        return True
        
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

                # TODO: take multicurrency into account
                
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

    def debit_storno(self, cr, uid, payment_line_id, amount,
                     currency, storno_retry=True, context=None):
        """
        The processing of a storno is triggered by a debit
        transfer on one of the company's bank accounts.
        This method offers to re-reconcile the original debit
        payment. For this purpose, we have registered that
        payment move on the payment line.

        Return the (now incomplete) reconcile id. The caller MUST
        re-reconcile this reconcile with the bank transfer and
        re-open the associated invoice.

        :param payment_line_id: the single payment line id
        :param amount: the (signed) amount debited from the bank account
        :param currency: the bank account's currency *browse object*
        :param boolean storno_retry: when True, attempt to reopen the invoice, \
        set the invoice to 'Debit denied' otherwise.
        :return: an incomplete reconcile for the caller to fill
        :rtype: database id of an account.move.reconcile resource.
        """

        move_line_obj = self.pool.get('account.move.line')
        reconcile_obj = self.pool.get('account.move.reconcile')
        line = self.browse(cr, uid, payment_line_id)
        reconcile_id = False
        if (line.debit_move_line_id and not line.storno and
            self.pool.get('res.currency').is_zero(
                cr, uid, currency, (
                    (line.debit_move_line_id.credit or 0.0) -
                    (line.debit_move_line_id.debit or 0.0) + amount))):
            # Two different cases, full and partial
            # Both cases differ subtly in the procedure to follow
            # Needs refractoring, but why is this not in the OpenERP API?
            # Actually, given the nature of a direct debit order and storno,
            # we should not need to take partial into account on the side of
            # the debit_move_line.
            if line.debit_move_line_id.reconcile_partial_id:
                reconcile_id = line.debit_move_line_id.reconcile_partial_id.id
                attribute = 'reconcile_partial_id'
                if len(line.debit_move_line_id.reconcile_id.line_partial_ids) == 2:
                    # reuse the simple reconcile for the storno transfer
                    reconcile_obj.write(
                        cr, uid, reconcile_id, {
                            'line_id': [(6, 0, line.debit_move_line_id.id)],
                            'line_partial_ids': [(6, 0, [])],
                            }, context=context)
                else:
                    # split up the original reconcile in a partial one
                    # and a new one for reconciling the storno transfer
                    reconcile_obj.write(
                        cr, uid, reconcile_id, {
                            'line_partial_ids': [(3, line.debit_move_line_id.id)],
                            }, context=context)
                    reconcile_id = reconcile_obj.create(
                        cr, uid, {
                            'type': 'auto',
                            'line_id': [(6, 0, line.debit_move_line_id.id)],
                            }, context=context)
            elif line.debit_move_line_id.reconcile_id:
                reconcile_id = line.debit_move_line_id.reconcile_id.id
                if len(line.debit_move_line_id.reconcile_id.line_id) == 2:
                    # reuse the simple reconcile for the storno transfer
                    reconcile_obj.write(
                        cr, uid, reconcile_id, {
                            'line_id': [(6, 0, [line.debit_move_line_id.id])]
                            }, context=context)
                else:
                    # split up the original reconcile in a partial one
                    # and a new one for reconciling the storno transfer
                    partial_ids = [ 
                        x.id for x in line.debit_move_line_id.reconcile_id.line_id
                        if x.id != line.debit_move_line_id.id
                        ]
                    reconcile_obj.write(
                        cr, uid, reconcile_id, {
                            'line_partial_ids': [(6, 0, partial_ids)],
                            'line_id': [(6, 0, [])],
                            }, context=context)
                    reconcile_id = reconcile_obj.create(
                        cr, uid, {
                            'type': 'auto',
                            'line_id': [(6, 0, line.debit_move_line_id.id)],
                            }, context=context)
            # mark the payment line for storno processed
            if reconcile_id:
                self.write(cr, uid, [payment_line_id],
                           {'storno': True}, context=context)
                # put forth the invoice workflow
                if line.move_line_id.invoice:
                    activity = (storno_retry and 'open_test'
                                or 'invoice_debit_denied')
                    netsvc.LocalService("workflow").trg_validate(
                        uid, 'account.invoice', line.move_line_id.invoice.id,
                        activity, cr)
        return reconcile_id

    def get_storno_account_id(self, cr, uid, payment_line_id, amount,
                     currency, context=None):
        """
        Check the match of the arguments, and return the account associated
        with the storno.
        Used in account_banking interactive mode

        :param payment_line_id: the single payment line id
        :param amount: the (signed) amount debited from the bank account
        :param currency: the bank account's currency *browse object*
        :return: an account if there is a full match, False otherwise
        :rtype: database id of an account.account resource.
        """

        line = self.browse(cr, uid, payment_line_id)
        account_id = False
        if (line.debit_move_line_id and not line.storno and
            self.pool.get('res.currency').is_zero(
                cr, uid, currency, (
                    (line.debit_move_line_id.credit or 0.0) -
                    (line.debit_move_line_id.debit or 0.0) + amount))):
            account_id = line.debit_move_line_id.account_id.id
        return account_id

    def debit_reconcile(self, cr, uid, payment_line_id, context=None):
        """
        Reconcile a debit order's payment line with the the move line
        that it is based on. Called from payment_order.action_sent().
        As the amount is derived directly from the counterpart move line,
        we do not expect a write off. Take partially reconcilions into
        account though.

        :param payment_line_id: the single id of the canceled payment line
        """

        if isinstance(payment_line_id, (list, tuple)):
            payment_line_id = payment_line_id[0]
        reconcile_obj = self.pool.get('account.move.reconcile')
        move_line_obj = self.pool.get('account.move.line')
        payment_line_record = self.browse(cr, uid, payment_line_id, context=context)

        debit_move_line = payment_line_record.debit_move_line_id
        torec_move_line = payment_line_record.move_line_id

        if payment_line_record.storno:
            raise osv.except_osv(
                _('Can not reconcile'),
                _('Cancelation of payment line \'%s\' has already been ' +
                  'processed') % payment_line_record.name)
        if (not debit_move_line or not torec_move_line):
            raise osv.except_osv(
                _('Can not reconcile'),
                _('No move line for line %s') % payment_line_record.name)     
        if torec_move_line.reconcile_id: # torec_move_line.reconcile_partial_id:
            raise osv.except_osv(
                _('Error'),
                _('Move line %s has already been reconciled') % 
                torec_move_line.name
                )
        if debit_move_line.reconcile_id or debit_move_line.reconcile_partial_id:
            raise osv.except_osv(
                _('Error'),
                _('Move line %s has already been reconciled') % 
                debit_move_line.name
                )

        def is_zero(total):
            return self.pool.get('res.currency').is_zero(
                cr, uid, debit_move_line.company_id.currency_id, total)

        line_ids = [debit_move_line.id, torec_move_line.id]
        if torec_move_line.reconcile_partial_id:
            line_ids = [
                x.id for x in torec_move_line.reconcile_partial_id.line_partial_ids] + [debit_move_line.id]

        total = move_line_obj.get_balance(cr, uid, line_ids)
        vals = {
            'type': 'auto',
            'line_id': is_zero(total) and [(6, 0, line_ids)] or [(6, 0, [])],
            'line_partial_ids': is_zero(total) and [(6, 0, [])] or [(6, 0, line_ids)],
            }

        if torec_move_line.reconcile_partial_id:
            reconcile_obj.write(
                cr, uid, debit_move_line.reconcile_partial_id.id,
                vals, context=context)
        else:
            reconcile_obj.create(
                cr, uid, vals, context=context)
        for line_id in line_ids:
            netsvc.LocalService("workflow").trg_trigger(
                uid, 'account.move.line', line_id, cr)

        # If a bank transaction of a storno was first confirmed
        # and now canceled (the invoice is now in state 'debit_denied'
        if torec_move_line.invoice:
            netsvc.LocalService("workflow").trg_validate(
                uid, 'account.invoice', torec_move_line.invoice.id,
                'undo_debit_denied', cr)



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
        payment = self.pool.get('payment.order').browse(
            cr, uid, context['active_id'], context=context)
        # Search for move line to pay:
        if payment.payment_order_type == 'debit':
            domain = [
                ('reconcile_id', '=', False),
                ('account_id.type', '=', 'receivable'),
                ('invoice_state', '!=', 'debit_denied'),
                ('amount_to_receive', '>', 0),
                ]
        else:
            domain = [
                ('reconcile_id', '=', False),
                ('account_id.type', '=', 'payable'),
                ('amount_to_pay', '>', 0)
                ]
        domain.append(('company_id', '=', payment.mode.company_id.id))
        # apply payment term filter
        if payment.mode.payment_term_ids:
            domain = domain + [
                ('payment_term_id', 'in', 
                 [term.id for term in payment.mode.payment_term_ids]
                 )
                ]
        # domain = [('reconcile_id', '=', False), ('account_id.type', '=', 'payable'), ('amount_to_pay', '>', 0)]
        ### end account_direct_debit ###

        domain = domain + ['|', ('date_maturity', '<=', search_due_date), ('date_maturity', '=', False)]
        line_ids = line_obj.search(cr, uid, domain, context=context)
        context.update({'line_ids': line_ids})
        model_data_ids = mod_obj.search(cr, uid,[('model', '=', 'ir.ui.view'), ('name', '=', 'view_create_payment_order_lines')], context=context)
        resource_id = mod_obj.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']
        return {'name': ('Entry Lines'),
                'context': context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'payment.order.create',
                'views': [(resource_id,'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
        }
payment_order_create()


                  
