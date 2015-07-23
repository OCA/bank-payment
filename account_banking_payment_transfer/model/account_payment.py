# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#              (C) 2011 - 2013 Therp BV (<http://therp.nl>).
#              (C) 2014 ACSONE SA (<http://acsone.eu>).
#              (C) 2014 Akretion (www.akretion.com)
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

from openerp import models, fields, api, _


class PaymentOrder(models.Model):
    '''
    Enable extra states for payment exports
    '''
    _inherit = 'payment.order'

    @api.multi
    def get_partial_reconcile_ids(self):
        self.ensure_one()
        reconcile_partial_ids = [line.move_line_id.reconcile_partial_id.id
                                 for line in self.line_ids if
                                 line.move_line_id.reconcile_partial_id.id]
        return reconcile_partial_ids

    @api.one
    def get_partial_reconcile_count(self):
        self.partial_reconcile_count = len(self.get_partial_reconcile_ids())

    date_scheduled = fields.Date(states={
        'sent': [('readonly', True)],
        'rejected': [('readonly', True)],
        'done': [('readonly', True)],
        })
    reference = fields.Char(states={
        'sent': [('readonly', True)],
        'rejected': [('readonly', True)],
        'done': [('readonly', True)],
        })
    mode = fields.Many2one(states={
        'sent': [('readonly', True)],
        'rejected': [('readonly', True)],
        'done': [('readonly', True)],
        })
    state = fields.Selection(selection_add=[
        ('sent', 'Sent'),
        ('rejected', 'Rejected'),
        ], string='State')
    line_ids = fields.One2many(states={
        'open': [('readonly', True)],
        'cancel': [('readonly', True)],
        'sent': [('readonly', True)],
        'rejected': [('readonly', True)],
        'done': [('readonly', True)]
        })
    user_id = fields.Many2one(states={
        'sent': [('readonly', True)],
        'rejected': [('readonly', True)],
        'done': [('readonly', True)]
        })
    date_prefered = fields.Selection(states={
        'sent': [('readonly', True)],
        'rejected': [('readonly', True)],
        'done': [('readonly', True)]
        })
    date_sent = fields.Date(string='Send date', readonly=True)
    partial_reconcile_count = fields\
        .Integer(string='Partial Reconciles Counter',
                 compute='get_partial_reconcile_count')

    @api.multi
    def action_rejected(self):
        return True

    @api.multi
    def action_done(self):
        for line in self.line_ids:
            line.date_done = fields.Date.context_today(self)
        return super(PaymentOrder, self).action_done()

    @api.multi
    def _get_transfer_move_lines(self):
        """
        Get the transfer move lines (on the transfer account).
        """
        res = []
        for order in self:
            for order_line in order.line_ids:
                move_line = order_line.transfer_move_line_id
                if move_line:
                    res.append(move_line)
        return res

    @api.multi
    def get_transfer_move_line_ids(self, *args):
        '''Used in the workflow for trigger_expr_id'''
        return [move_line.id for move_line in self._get_transfer_move_lines()]

    @api.multi
    def test_done(self):
        """
        Test if all moves on the transfer account are reconciled.

        Called from the workflow to move to the done state when
        all transfer move have been reconciled through bank statements.
        """
        return all([move_line.reconcile_id for move_line in
                    self._get_transfer_move_lines()])

    @api.multi
    def test_undo_done(self):
        return not self.test_done()

    @api.multi
    def _prepare_transfer_move(self):
        vals = {
            'journal_id': self.mode.transfer_journal_id.id,
            'ref': '%s %s' % (
                self.payment_order_type[:3].upper(), self.reference)
            }
        return vals

    @api.multi
    def _prepare_move_line_transfer_account(
            self, amount, move, payment_lines, labels):
        if len(payment_lines) == 1:
            partner_id = payment_lines[0].partner_id.id
            name = _('%s line %s') % (labels[self.payment_order_type],
                                      payment_lines[0].name)
            if payment_lines[0].move_line_id.id and\
                    payment_lines[0].move_line_id.move_id.state != 'draft':
                name = "%s (%s)" % (name,
                                    payment_lines[0].move_line_id.move_id.name)
            elif payment_lines[0].ml_inv_ref.id:
                name = "%s (%s)" % (name,
                                    payment_lines[0].ml_inv_ref.number)
        else:
            partner_id = False
            name = '%s %s' % (
                labels[self.payment_order_type], self.reference)
        date_maturity = payment_lines[0].date
        vals = {
            'name': name,
            'move_id': move.id,
            'partner_id': partner_id,
            'account_id': self.mode.transfer_account_id.id,
            'credit': (self.payment_order_type == 'payment' and
                       amount or 0.0),
            'debit': (self.payment_order_type == 'debit' and
                      amount or 0.0),
            'date_maturity': date_maturity,
        }
        return vals

    @api.multi
    def _prepare_move_line_partner_account(self, line, move, labels):
        if line.move_line_id:
            account_id = line.move_line_id.account_id.id
        else:
            if self.payment_order_type == 'debit':
                account_id = line.partner_id.property_account_receivable.id
            else:
                account_id = line.partner_id.property_account_payable.id
        vals = {
            'name': _('%s line %s') % (
                labels[self.payment_order_type], line.name),
            'move_id': move.id,
            'partner_id': line.partner_id.id,
            'account_id': account_id,
            'credit': (self.payment_order_type == 'debit' and
                       line.amount or 0.0),
            'debit': (self.payment_order_type == 'payment' and
                      line.amount or 0.0),
            }
        return vals

    @api.multi
    def action_sent_no_move_line_hook(self, pay_line):
        """This function is designed to be inherited"""
        return

    @api.multi
    def _create_move_line_partner_account(self, line, move, labels):
        """This method is designed to be inherited in a custom module"""

        # TODO: take multicurrency into account
        aml_obj = self.env['account.move.line']
        # create the payment/debit counterpart move line
        # on the partner account
        partner_ml_vals = self._prepare_move_line_partner_account(
            line, move, labels)
        partner_move_line = aml_obj.create(partner_ml_vals)

        # register the payment/debit move line
        # on the payment line and call reconciliation on it
        line.write({'transit_move_line_id': partner_move_line.id})

    @api.multi
    def _reconcile_payment_lines(self, payment_lines):
        for line in payment_lines:
            if line.move_line_id:
                line.debit_reconcile()
            else:
                self.action_sent_no_move_line_hook(line)

    @api.one
    def action_sent(self):
        """
        Create the moves that pay off the move lines from
        the debit order. This happens when the debit order file is
        generated.
        """
        am_obj = self.env['account.move']
        aml_obj = self.env['account.move.line']
        labels = {
            'payment': _('Payment order'),
            'debit': _('Direct debit order'),
            }
        if self.mode.transfer_journal_id and self.mode.transfer_account_id:
            # prepare a dict "trfmoves" that can be used when
            # self.mode.transfer_move_option = date or line
            # key = unique identifier (date or True or line.id)
            # value = [pay_line1, pay_line2, ...]
            trfmoves = {}
            if self.mode.transfer_move_option == 'line':
                for line in self.line_ids:
                    trfmoves[line.id] = [line]
            else:
                if self.date_prefered in ('now', 'fixed'):
                    trfmoves[True] = []
                    for line in self.line_ids:
                        trfmoves[True].append(line)
                else:  # date_prefered == due
                    for line in self.line_ids:
                        if line.date in trfmoves:
                            trfmoves[line.date].append(line)
                        else:
                            trfmoves[line.date] = [line]

            for identifier, lines in trfmoves.iteritems():
                mvals = self._prepare_transfer_move()
                move = am_obj.create(mvals)
                total_amount = 0
                for line in lines:
                    total_amount += line.amount
                    self._create_move_line_partner_account(line, move, labels)
                # create the payment/debit move line on the transfer account
                trf_ml_vals = self._prepare_move_line_transfer_account(
                    total_amount, move, lines, labels)
                aml_obj.create(trf_ml_vals)
                self._reconcile_payment_lines(lines)

                # consider entry_posted on account_journal
                if move.journal_id.entry_posted:
                    # post account move
                    move.post()

        # State field is written by act_sent_wait
        self.write({'date_sent': fields.Date.context_today(self)})
        return True

    @api.multi
    def partial(self):
        self.ensure_one()
        view_id = self.env.ref('account.view_move_line_tree').id
        reconcile_partial_ids = self.get_partial_reconcile_ids()
        reconcile_partial_domain = [('reconcile_partial_id', 'in',
                                     reconcile_partial_ids)]
        return {
            'name': _('Partial Reconcile Moves Line'),
            'context': self.env.context,
            'domain': reconcile_partial_domain,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'views': [(view_id, 'tree')],
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
