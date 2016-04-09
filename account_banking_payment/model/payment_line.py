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
from openerp import netsvc
from openerp.tools.translate import _


class payment_line(orm.Model):
    '''
    Add some fields; make destination bank account
    mandatory, as it makes no sense to send payments into thin air.
    Edit: Payments can be by cash too, which is prohibited by mandatory bank
    accounts.
    '''
    _inherit = 'payment.line'
    _columns = {
        'msg': fields.char('Message', size=255, required=False, readonly=True),
        'date_done': fields.date(
            'Date Confirmed', select=True, readonly=True),
        'transit_move_line_id': fields.many2one(
            # this line is part of the credit side of move 2a
            # from the documentation
            'account.move.line', 'Debit move line',
            readonly=True,
            help="Move line through which the debit order pays the invoice",
        ),
    }

    _defaults = {
        'msg': '',
    }

    """
    Hooks for processing direct debit orders, such as implemented in
    account_direct_debit module.
    """
    def get_storno_account_id(self, cr, uid, payment_line_id, amount,
                              currency_id, context=None):
        """
        Hook for verifying a match of the payment line with the amount.
        Return the account associated with the storno.
        Used in account_banking interactive mode
        :param payment_line_id: the single payment line id
        :param amount: the (signed) amount debited from the bank account
        :param currency: the bank account's currency *browse object*
        :return: an account if there is a full match, False otherwise
        :rtype: database id of an account.account resource.
        """

        return False

    def debit_storno(self, cr, uid, payment_line_id, amount,
                     currency_id, storno_retry=True, context=None):
        """
        Hook for handling a canceled item of a direct debit order.
        Presumably called from a bank statement import routine.

        Decide on the direction that the invoice's workflow needs to take.
        You may optionally return an incomplete reconcile for the caller
        to reconcile the now void payment.

        :param payment_line_id: the single payment line id
        :param amount: the (negative) amount debited from the bank account
        :param currency: the bank account's currency *browse object*
        :param boolean storno_retry: whether the storno is considered fatal \
        or not.
        :return: an incomplete reconcile for the caller to fill
        :rtype: database id of an account.move.reconcile resource.
        """

        return False

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
        payment_line = self.browse(cr, uid, payment_line_id, context=context)

        transit_move_line = payment_line.transit_move_line_id
        torec_move_line = payment_line.move_line_id

        if (not transit_move_line or not torec_move_line):
            raise orm.except_orm(
                _('Can not reconcile'),
                _('No move line for line %s') % payment_line.name
            )
        if torec_move_line.reconcile_id:
            raise orm.except_orm(
                _('Error'),
                _('Move line %s has already been reconciled') %
                torec_move_line.name
            )
        if (transit_move_line.reconcile_id or
                transit_move_line.reconcile_partial_id):
            raise orm.except_orm(
                _('Error'),
                _('Move line %s has already been reconciled') %
                transit_move_line.name
            )

        def is_zero(total):
            return self.pool.get('res.currency').is_zero(
                cr, uid, transit_move_line.company_id.currency_id, total)

        line_ids = [transit_move_line.id, torec_move_line.id]
        if torec_move_line.reconcile_partial_id:
            line_ids = [
                x.id for x in
                torec_move_line.reconcile_partial_id.line_partial_ids
            ] + [transit_move_line.id]

        total = move_line_obj.get_balance(cr, uid, line_ids)
        vals = {
            'type': 'auto',
            'line_id': is_zero(total) and [(6, 0, line_ids)] or [(6, 0, [])],
            'line_partial_ids': (is_zero(total) and
                                 [(6, 0, [])] or
                                 [(6, 0, line_ids)]),
        }

        if torec_move_line.reconcile_partial_id:
            reconcile_obj.write(
                cr, uid, transit_move_line.reconcile_partial_id.id,
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
