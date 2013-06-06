# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>).
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
from openerp.tools.translate import _
from openerp import netsvc

class banking_export_aggregate(orm.TransientModel):
    _name = 'banking.export.aggregate'
    _columns = {
        'payment_order_id': fields.many2one(
            'payment.order', 'Payment order',
            required=True),
        'reference': fields.char(
            'Reference', size=24),
        }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if not vals.get('payment_order_id'):
            if not context.get('active_ids'):
                raise orm.except_orm(
                    _('Error'),
                    _('Please select a payment order'))
            if len(context['active_ids']) > 1:
                raise orm.except_orm(
                    _('Error'),
                    _('Please only select a single payment order'))
            vals['payment_order_id'] = context['active_ids'][0]
        return self.create(
            cr, uid, vals, context=context)

    def reconcile_lines(self, cr, uid, move_line_ids, context=None):
        """
        Reconcile move lines lines, really. Talk about core functionality
        """
        reconcile_obj = self.pool.get('account.move.reconcile')
        account_move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        lines = account_move_line_obj.browse(cr, uid, move_line_ids, context=context)

        for line in lines[1:]:
            if line.account_id != lines[0].account_id:
                raise orm.except_orm(
                    _('Error'),
                    _('Cannot reconcile between different accounts'))

        if any(lines, 
               lambda line: line.reconcile_id and line.reconcile_id.line_id):
            raise orm.except_orm(
                _('Error'),
                _('Line is already fully reconciled'))
            
        currency = lines[0].company_id.currency_id

        partials = []
        line_ids = []
        for line in lines:
            if line.id not in line_ids:
                line_ids.append(line.id)
            if line.reconcile_partial_id:
                line_ids += line.reconcile_partial_id.line_partial_ids
                if line.reconcile_partial_id.id not in partials:
                    partials.append(line.reconcile_partial_id.id)

        total = account_move_line_obj.get_balance(cr, uid, line_ids)
        is_zero = currency_obj.is_zero(cr, uid, currency, total)

        vals = {
            'type': 'auto',
            'line_id': is_zero and [(6, 0, line_ids)] or [(6, 0, [])],
            'line_partial_ids': is_zero and [(6, 0, [])] or [(6, 0, line_ids)],
            }

        if partials:
            if len(partials) > 1:
                reconcile_obj.unlink(
                    cr, uid, partials[1:], context=context)
            reconcile_obj.write(
                cr, uid, partials[0],
                vals, context=context)
        else:
            reconcile_obj.create(
                cr, uid, vals, context=context)

        for line_id in line_ids:
            netsvc.LocalService("workflow").trg_trigger(
                uid, 'account.move.line', line_id, cr)
        return True

    def create_aggregate_order(self, cr, uid, ids, context=None):
        wiz = self.browse(cr, uid, ids[0], context=context)
        account_move_line_obj = self.pool.get('account.move.line')
        account_move_obj = self.pool.get('account.move')
        payment_order_obj = self.pool.get('payment.order')
        payment_order_line_obj = self.pool.get('payment.order.line')
        payment_order_ids = context.get('active_ids', [])
        if not payment_order_ids:
            raise orm.except_orm(
                _('Error'),
                _('Please select a payment order'))
        if len(payment_order_ids) > 1:
            raise orm.except_orm(
                _('Error'),
                _('This operation can only be performed on a single payment order'))
        order = payment_order_obj.browse(
            cr, uid, payment_order_ids[0], context=context)
        if not (order.mode.transfer_journal_id and
                order.mode.transfer_account_id):
            raise orm.except_orm(
                _('Error'),
                _('Transfer journal or account are not filled '
                  'in on the payment mode'))

        move_id = account_move_obj.create(cr, uid, {
                'journal_id': order.mode.transfer_journal_id.id,
                'name': 'Aggregate Payment Order %s' % order.reference,
                'reference': order.reference,
                }, context=context)

        counter_move_line_ids = []
        for line in order.line_ids:
            # basic checks
            if not line.move_line_id:
                raise orm.except_orm(
                    _('Error'),
                    _('No move line provided for line %s') % line.name)
            if line.move_line_id.reconcile_id:
                raise orm.except_orm(
                    _('Error'),
                    _('Move line %s has already been paid/reconciled') % 
                    line.move_line_id.name
                    )

            # TODO: take multicurrency into account
            
            # create the move line on the transfer account
            vals = {
                'name': 'Aggregate payment for %s' % (
                    line.move_line_id.invoice and 
                    line.move_line_id.invoice.number or 
                    line.move_line_id.name),
                'move_id': move_id,
                'partner_id': line.partner_id and line.partner_id.id or False,
                'account_id': order.mode.transfer_account_id.id,
                'credit': line.amount,
                'debit': 0.0,
                'date': fields.date.context_today(self, cr, uid, context=context),
                }
            counter_move_line_id = account_move_line_obj.create(
                cr, uid, vals, context=context)
            counter_move_line_ids.append(counter_move_line_id)

            # create the debit move line on the receivable account
            vals.update({
                    'account_id': line.move_line_id.account_id.id,
                    'credit': 0.0,
                    'debit': line.amount,
                    })               
            reconcile_move_line_id = account_move_line_obj.create(
                cr, uid, vals, context=context)
                
            self.reconcile_lines(
                cr, uid, [reconcile_move_line_id, counter_move_line_id],
                context=context)

        total = account_move_line_obj.get_balance(
            cr, uid, counter_move_line_ids)

        vals = {
            'name': 'Aggregate payment for %s' % (
                line.move_line_id.invoice and 
                line.move_line_id.invoice.number or 
                line.move_line_id.name),
            'move_id': move_id,
            'partner_id': order.mode.aggregate_partner_id.id,
            'account_id': order.mode.transfer_account_id.id,
            'credit': 0.0,
            'debit': total,
            'date': fields.date.context_today(self, cr, uid, context=context),
            }
        aggregate_move_line_id = account_move_line_obj.create(
            cr, uid, vals, context=context)

        self.reconcile_lines(
            cr, uid, counter_move_line_ids + [aggregate_move_line_id],
            context=context)

        # create the credit move line on the aggregate partner
        vals.update({
                'account_id': order.mode.aggregate_partner_id.property_account_payable.id,
                'partner_id': order.mode.aggregate_partner_id.id,
                'credit': total,
                'debit': 0.0,
                })               

        payable_move_line = account_move_line_obj.browse(
            cr, uid,
            account_move_line_obj.create(
                cr, uid, vals, context=context),
            context=context)

        account_move_obj.post(cr, uid, [move_id], context=context)

        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'payment.order', order.id, 'sent', cr)
        wf_service.trg_validate(uid, 'payment.order', order.id, 'done', cr)
        order.refresh()
        if order.state != 'done':
            raise orm.except_orm(
                _('Error'),
                _('Payment order workflow does not go into state "done"'))

        payment_order_id = payment_order_obj.create(
            cr, uid, {
                'company_id': order.company_id.id,
                'mode': order.mode.aggregate_mode_id.id,
                }, context=context)

        lines2bank = payment_order_line_obj.line2bank(
            cr, uid, [payable_move_line.id], order.mode.id, context)

        payment_order_line_obj.create(cr, uid,{
                'move_line_id': payable_move_line.id,
                'amount_currency': payable_move_line.amount_to_pay,
                'bank_id': lines2bank.get(payable_move_line.id),
                'order_id': payment_order_id,
                'partner_id': order.mode.aggregate_partner_id.id,
                'communication': False,
                'communication2': payable_move_line.ref,
                'state': 'normal',
                'date': False,
                'currency': (line.journal_id.currency.id or
                             line.journal_id.company_id.currency_id.id),
                }, context=context)

        return {
            'name': payment_order_obj._description,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': payment_order_obj._name,
            'domain': [],
            'context': context,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': payment_order_id,
            'nodestroy': True,
            }
