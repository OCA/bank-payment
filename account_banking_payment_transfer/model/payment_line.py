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
from openerp import models, fields, workflow, api, exceptions
from openerp.tools.translate import _


class PaymentLine(models.Model):
    '''
    Add some fields; make destination bank account
    mandatory, as it makes no sense to send payments into thin air.
    Edit: Payments can be by cash too, which is prohibited by mandatory bank
    accounts.
    '''
    _inherit = 'payment.line'

    @api.multi
    def _get_transfer_move_line(self):
        for order_line in self:
            if order_line.transit_move_line_id:
                order_type = order_line.order_id.payment_order_type
                trf_lines = order_line.transit_move_line_id.move_id.line_id
                for move_line in trf_lines:
                    if order_type == 'debit' and move_line.debit > 0:
                        order_line.transfer_move_line_id = move_line
                    elif order_type == 'payment' and move_line.credit > 0:
                        order_line.transfer_move_line_id = move_line

    msg = fields.Char('Message', required=False, readonly=True, default='')
    date_done = fields.Date('Date Confirmed', select=True, readonly=True)
    transit_move_line_id = fields.Many2one(
        'account.move.line', string='Transfer move line', readonly=True,
        help="Move line through which the payment/debit order "
        "pays the invoice")
    transfer_move_line_id = fields.Many2one(
        'account.move.line', compute='_get_transfer_move_line',
        string='Transfer move line counterpart',
        help="Counterpart move line on the transfer account")

    """
    Hooks for processing direct debit orders, such as implemented in
    account_direct_debit module.
    """
    @api.multi
    def get_storno_account_id(self, amount, currency_id):
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

    @api.multi
    def debit_storno(self, amount, currency_id, storno_retry=True):
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

    @api.one
    def debit_reconcile(self):
        """
        Reconcile a debit order's payment line with the the move line
        that it is based on. Called from payment_order.action_sent().
        As the amount is derived directly from the counterpart move line,
        we do not expect a write off. Take partial reconciliations into
        account though.

        :param payment_line_id: the single id of the canceled payment line
        """

        transit_move_line = self.transit_move_line_id
        torec_move_line = self.move_line_id

        if (not transit_move_line or not torec_move_line):
            raise exceptions.except_orm(
                _('Can not reconcile'),
                _('No move line for line %s') % self.name
            )
        if torec_move_line.reconcile_id:
            raise exceptions.except_orm(
                _('Error'),
                _('Move line %s has already been reconciled') %
                torec_move_line.name
                )
        if (transit_move_line.reconcile_id or
                transit_move_line.reconcile_partial_id):
            raise exceptions.except_orm(
                _('Error'),
                _('Move line %s has already been reconciled') %
                transit_move_line.name
            )

        line_ids = [transit_move_line.id, torec_move_line.id]
        self.env['account.move.line'].browse(line_ids).reconcile_partial(
            type='auto')

        # If a bank transaction of a storno was first confirmed
        # and now canceled (the invoice is now in state 'debit_denied'
        if torec_move_line.invoice:
            workflow.trg_validate(
                self.env.uid, 'account.invoice', torec_move_line.invoice.id,
                'undo_debit_denied', self.env.cr)
