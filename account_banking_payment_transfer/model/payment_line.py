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

    msg = fields.Char('Message', required=False, readonly=True, default='')
    date_done = fields.Date('Date Confirmed', select=True, readonly=True)


class BankPaymentLine(models.Model):
    _inherit = 'bank.payment.line'

    transit_move_line_id = fields.Many2one(
        'account.move.line', string='Transfer move line', readonly=True,
        help="Move line through which the payment/debit order "
        "pays the invoice")
    transfer_move_line_id = fields.Many2one(
        'account.move.line', compute='_get_transfer_move_line',
        string='Transfer move line counterpart',
        help="Counterpart move line on the transfer account")

    @api.multi
    def _get_transfer_move_line(self):
        for bank_line in self:
            if bank_line.transit_move_line_id:
                order_type = bank_line.order_id.payment_order_type
                trf_lines = bank_line.transit_move_line_id.move_id.line_id
                for move_line in trf_lines:
                    if order_type == 'debit' and move_line.debit > 0:
                        bank_line.transfer_move_line_id = move_line
                    elif order_type == 'payment' and move_line.credit > 0:
                        bank_line.transfer_move_line_id = move_line

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

#        if (not transit_move_line or not torec_move_line):
#            raise exceptions.UserError(
#                _('Can not reconcile: no move line for line %s') % self.name
#            )
#        if torec_move_line.reconcile_id:
#            raise exceptions.UserError(
#                _('Move line %s has already been reconciled') %
#                torec_move_line.name
#                )
#        if (transit_move_line.reconcile_id or
#                transit_move_line.reconcile_partial_id):
#            raise exceptions.UserError(
#                _('Move line %s has already been reconciled') %
#                transit_move_line.name
#            )

        lines_to_rec = transit_move_line
        for payment_line in self.payment_line_ids:
            lines_to_rec += payment_line.move_line_id

        lines_to_rec.reconcile_partial(type='auto')
