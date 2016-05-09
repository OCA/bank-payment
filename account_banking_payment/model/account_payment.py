# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#              (C) 2011 - 2013 Therp BV (<http://therp.nl>).
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

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp import netsvc


class payment_order(orm.Model):
    '''
    Enable extra states for payment exports
    '''
    _inherit = 'payment.order'

    _columns = {
        'date_scheduled': fields.date(
            'Scheduled date if fixed',
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
            help='Select a date if you have chosen Preferred Date to be fixed.'
        ),
        'reference': fields.char(
            'Reference', size=128, required=True,
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'mode': fields.many2one(
            'payment.mode', 'Payment mode', select=True, required=True,
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
            help='Select the Payment Mode to be applied.',
        ),
        'state': fields.selection(
            [
                ('draft', 'Draft'),
                ('open', 'Confirmed'),
                ('cancel', 'Cancelled'),
                ('sent', 'Sent'),
                ('rejected', 'Rejected'),
                ('done', 'Done'),
            ],
            'State', select=True
        ),
        'line_ids': fields.one2many(
            'payment.line', 'order_id', 'Payment lines',
            states={
                'open': [('readonly', True)],
                'cancel': [('readonly', True)],
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'user_id': fields.many2one(
            'res.users', 'User', required=True,
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'date_prefered': fields.selection(
            [
                ('now', 'Directly'),
                ('due', 'Due date'),
                ('fixed', 'Fixed date')
            ],
            "Preferred date", change_default=True, required=True,
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
            help=("Choose an option for the Payment Order:'Fixed' stands for "
                  "a date specified by you.'Directly' stands for the direct "
                  "execution.'Due date' stands for the scheduled date of "
                  "execution.")
        ),
        'date_sent': fields.date('Send date', readonly=True),
    }

    def _write_payment_lines(self, cr, uid, ids, **kwargs):
        '''
        ORM method for setting attributes of corresponding payment.line
        objects.
        Note that while this is ORM compliant, it is also very ineffecient due
        to the absence of filters on writes and hence the requirement to
        filter on the client(=OpenERP server) side.
        '''
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        payment_line_obj = self.pool.get('payment.line')
        line_ids = payment_line_obj.search(
            cr, uid, [
                ('order_id', 'in', ids)
            ])
        payment_line_obj.write(cr, uid, line_ids, kwargs)

    def action_rejected(self, cr, uid, ids, *args):
        '''
        Set both self and payment lines to state 'rejected'.
        '''
        wf_service = netsvc.LocalService('workflow')
        for id in ids:
            wf_service.trg_validate(uid, 'payment.order', id, 'rejected', cr)
        return True

    def set_done(self, cr, uid, ids, *args):
        '''
        Extend standard transition to update children as well.
        '''
        self._write_payment_lines(
            cr, uid, ids,
            date_done=fields.date.context_today(self, cr, uid))
        return super(payment_order, self).set_done(
            cr, uid, ids, *args
        )

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
        if not order.line_ids[0].transit_move_line_id:
            wf_service = netsvc.LocalService('workflow')
            wf_service.trg_validate(
                uid, 'payment.order', payment_order_id, 'done', cr)
            return False
        for order_line in order.line_ids:
            for line in order_line.transit_move_line_id.move_id.line_id:
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

    def debit_unreconcile_transfer(
            self, cr, uid, payment_order_id, reconcile_id, amount, currency,
            context=None):
        """
        Due to a cancelled bank statements import, unreconcile the move on
        the transfer account. Delegate the conditions to the workflow.
        Raise on failure for rollback.

        Workflow appears to return False even on success so we just check
        the order's state that we know to be set to 'sent' in that case.
        """
        self.pool.get('account.move.reconcile').unlink(
            cr, uid, [reconcile_id], context=context)
        netsvc.LocalService('workflow').trg_validate(
            uid, 'payment.order', payment_order_id, 'undo_done', cr)
        state = self.pool.get('payment.order').read(
            cr, uid, payment_order_id, ['state'], context=context)['state']
        if state != 'sent':
            raise orm.except_orm(
                _("Cannot unreconcile"),
                _("Cannot unreconcile payment order: "
                  "Workflow will not allow it."))
        return True

    def test_undo_done(self, cr, uid, ids, context=None):
        """
        Called from the workflow. Used to unset done state on
        payment orders that were reconciled with bank transfers
        which are being cancelled.

        Test if the payment order has not been reconciled. Depends
        on the restriction that transit move lines should use an
        account of type 'other', and on the restriction of payment and
        debit orders that they only take moves on accounts
        payable/receivable.
        """
        for order in self.browse(cr, uid, ids, context=context):
            for order_line in order.line_ids:
                if order_line.transit_move_line_id.move_id:
                    for line in \
                            order_line.transit_move_line_id.move_id.line_id:
                        if (line.account_id.type == 'other' and
                                line.reconcile_id):
                            return False
        return True

    def _prepare_transfer_move(
            self, cr, uid, order, line, labels, context=None):
        vals = {
            'journal_id': order.mode.transfer_journal_id.id,
            'name': '%s %s' % (labels[order.payment_order_type],
                               line.move_line_id and
                               line.move_line_id.move_id.name or
                               line.communication),
            'ref': '%s %s' % (order.payment_order_type[:3].upper(),
                              line.move_line_id and
                              line.move_line_id.move_id.name or
                              line.communication),
        }
        return vals

    def _prepare_move_line_transfer_account(
            self, cr, uid, order, line, move_id, labels, context=None):
        vals = {
            'name': _('%s for %s') % (
                labels[order.payment_order_type],
                line.move_line_id and (line.move_line_id.invoice and
                                       line.move_line_id.invoice.number or
                                       line.move_line_id.name) or
                line.communication),
            'move_id': move_id,
            'partner_id': False,
            'account_id': order.mode.transfer_account_id.id,
            'credit': (order.payment_order_type == 'payment' and
                       line.amount or 0.0),
            'debit': (order.payment_order_type == 'debit' and
                      line.amount or 0.0),
            'date': fields.date.context_today(
                self, cr, uid, context=context),
        }
        return vals

    def _update_move_line_partner_account(
            self, cr, uid, order, line, vals, context=None):
        vals.update({
            'partner_id': line.partner_id.id,
            'account_id': (line.move_line_id and
                           line.move_line_id.account_id.id or
                           False),
            # if not line.move_line_id, the field 'account_id' must be set by
            # another module that inherit this function, like for example in
            # the module purchase_payment_order
            'credit': (order.payment_order_type == 'debit' and
                       line.amount or 0.0),
            'debit': (order.payment_order_type == 'payment' and
                      line.amount or 0.0),
        })
        return vals

    def action_sent_no_move_line_hook(self, cr, uid, pay_line, context=None):
        """This function is designed to be inherited"""
        return

    def action_sent(self, cr, uid, ids, context=None):
        """
        Create the moves that pay off the move lines from
        the debit order. This happens when the debit order file is
        generated.
        """
        account_move_obj = self.pool.get('account.move')
        account_move_line_obj = self.pool.get('account.move.line')
        payment_line_obj = self.pool.get('payment.line')
        labels = {
            'payment': _('Payment order'),
            'debit': _('Direct debit order'),
        }
        for order in self.browse(cr, uid, ids, context=context):
            if not order.mode.transfer_journal_id or \
                    not order.mode.transfer_account_id:
                continue
            for line in order.line_ids:
                # basic checks
                if line.move_line_id and line.move_line_id.reconcile_id:
                    raise orm.except_orm(
                        _('Error'),
                        _('Move line %s has already been paid/reconciled')
                        % line.move_line_id.name)

                move_id = account_move_obj.create(
                    cr, uid, self._prepare_transfer_move(
                        cr, uid, order, line, labels, context=context),
                    context=context)

                # TODO: take multicurrency into account

                # create the debit move line on the transfer account
                ml_vals = self._prepare_move_line_transfer_account(
                    cr, uid, order, line, move_id, labels, context=context)
                account_move_line_obj.create(cr, uid, ml_vals, context=context)

                # create the debit move line on the partner account
                self._update_move_line_partner_account(
                    cr, uid, order, line, ml_vals, context=context)
                reconcile_move_line_id = account_move_line_obj.create(
                    cr, uid, ml_vals, context=context)

                # register the debit move line on the payment line
                # and call reconciliation on it
                payment_line_obj.write(
                    cr, uid, line.id,
                    {'transit_move_line_id': reconcile_move_line_id},
                    context=context)

                if line.move_line_id:
                    payment_line_obj.debit_reconcile(
                        cr, uid, line.id, context=context)
                else:
                    self.action_sent_no_move_line_hook(
                        cr, uid, line, context=context)
                account_move_obj.post(cr, uid, [move_id], context=context)

        # State field is written by act_sent_wait
        self.write(
            cr, uid, ids,
            {
                'date_sent': fields.date.context_today(
                    self, cr, uid, context=context),
            },
            context=context)

        return True
