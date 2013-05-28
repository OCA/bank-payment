# -*- coding: utf-8 -*-
from openerp.osv import orm, fields
import netsvc
from tools.translate import _

class payment_line(orm.Model):
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
        Raise if a payment line is passed for which storno is True
        """
        if isinstance(payment_line_id, (list, tuple)):
            payment_line_id = payment_line_id[0]
        payment_line = self.read(
            cr, uid, payment_line_id, ['storno', 'name'], context=context)
        if payment_line['storno']:
            raise orm.except_orm(
                _('Can not reconcile'),
                _('Cancelation of payment line \'%s\' has already been '
                  'processed') % payment_line['name'])
        return super(self, payment_line).debit_reconcile(
            cr, uid, payment_line_id, context=context)

    _columns = {
        'storno': fields.boolean(
            'Storno',
            readonly=True,
            help=("If this is true, the debit order has been canceled "
                  "by the bank or by the customer")),
        }


class payment_order_create(orm.Model_memory):
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
                ('invoice.state', '!=', 'debit_denied'),
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
                ('invoice.payment_term', 'in', 
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
