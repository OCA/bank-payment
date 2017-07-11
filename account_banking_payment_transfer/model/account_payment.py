# -*- coding: utf-8 -*-
# © 2009 EduSense BV (<http://www.edusense.nl>)
# © 2011-2013 Therp BV (<http://therp.nl>)
# © 2013-2014 ACSONE SA (<http://acsone.eu>).
# © 2014-2015 Akretion (www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


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
        if not self:
            return self.env['account.move.line']
        self.env.cr.execute(
            '''select ml.id from
            account_move_line ml join bank_payment_line pl
            on pl.transfer_move_line_id=ml.id
            where pl.order_id in %s''',
            (tuple(self.ids),),
        )
        return self.env['account.move.line'].browse(
            i for i, in self.env.cr.fetchall()
        )

    @api.multi
    def get_transfer_move_line_ids(self, *args):
        '''Used in the workflow for trigger_expr_id'''
        return self._get_transfer_move_lines().ids

    @api.multi
    def test_done(self):
        """
        Test if all moves on the transfer account are reconciled.

        Called from the workflow to move to the done state when
        all transfer move have been reconciled through bank statements.
        """
        transfer_move_ids = self.get_transfer_move_line_ids()
        if transfer_move_ids:
            self.env.cr.execute(
                '''select id from account_move_line
                where id in %s and reconcile_id is null''',
                (tuple(transfer_move_ids),)
            )
            return self.env.cr.rowcount == 0
        return True

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
            self, amount, move, bank_payment_lines, labels):
        if len(bank_payment_lines) == 1:
            partner_id = bank_payment_lines[0].partner_id.id
            name = _('%s bank line %s') % (labels[self.payment_order_type],
                                           bank_payment_lines[0].name)
        else:
            partner_id = False
            name = '%s %s' % (
                labels[self.payment_order_type], self.reference)
        date_maturity = bank_payment_lines[0].date
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
    def _prepare_move_line_partner_account(self, bank_line, move, labels):
        # TODO : ALEXIS check don't group if move_line_id.account_id
        # is not the same
        if bank_line.payment_line_ids[0].move_line_id:
            account_id =\
                bank_line.payment_line_ids[0].move_line_id.account_id.id
        else:
            if self.payment_order_type == 'debit':
                account_id =\
                    bank_line.partner_id.property_account_receivable.id
            else:
                account_id = bank_line.partner_id.property_account_payable.id
        vals = {
            'name': _('%s line %s') % (
                labels[self.payment_order_type], bank_line.name),
            'move_id': move.id,
            'partner_id': bank_line.partner_id.id,
            'account_id': account_id,
            'credit': (self.payment_order_type == 'debit' and
                       bank_line.amount_currency or 0.0),
            'debit': (self.payment_order_type == 'payment' and
                      bank_line.amount_currency or 0.0),
            }
        return vals

    @api.multi
    def action_sent_no_move_line_hook(self, pay_line):
        """This function is designed to be inherited"""
        return

    @api.multi
    def _create_move_line_partner_account(self, bank_line, move, labels):
        """This method is designed to be inherited in a custom module"""
        # TODO: take multicurrency into account
        company_currency = self.env.user.company_id.currency_id
        if bank_line.currency != company_currency:
            raise UserError(_(
                "Cannot generate the transfer move when "
                "the currency of the payment (%s) is not the "
                "same as the currency of the company (%s). This "
                "is not supported for the moment.")
                % (bank_line.currency.name, company_currency.name))
        aml_obj = self.env['account.move.line']
        # create the payment/debit counterpart move line
        # on the partner account
        partner_ml_vals = self._prepare_move_line_partner_account(
            bank_line, move, labels)
        partner_move_line = aml_obj.create(partner_ml_vals)

        # register the payment/debit move line
        # on the payment line and call reconciliation on it
        bank_line.write({'transit_move_line_id': partner_move_line.id})

    @api.multi
    def _reconcile_payment_lines(self, bank_payment_lines):
        for bline in bank_payment_lines:
            if all([pline.move_line_id for pline in bline.payment_line_ids]):
                bline.debit_reconcile()
            else:
                self.action_sent_no_move_line_hook(bline)

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
            'payment': _('Payment'),
            'debit': _('Direct debit'),
            }
        if self.mode.transfer_journal_id and self.mode.transfer_account_id:
            # prepare a dict "trfmoves" that can be used when
            # self.mode.transfer_move_option = date or line
            # key = unique identifier (date or True or line.id)
            # value = [pay_line1, pay_line2, ...]
            trfmoves = {}
            for bline in self.bank_line_ids:
                hashcode = bline.move_line_transfer_account_hashcode()
                if hashcode in trfmoves:
                    trfmoves[hashcode].append(bline)
                else:
                    trfmoves[hashcode] = [bline]

            for hashcode, blines in trfmoves.iteritems():
                mvals = self._prepare_transfer_move()
                move = am_obj.create(mvals)
                total_amount = 0
                for bline in blines:
                    total_amount += bline.amount_currency
                    self._create_move_line_partner_account(bline, move, labels)
                # create the payment/debit move line on the transfer account
                trf_ml_vals = self._prepare_move_line_transfer_account(
                    total_amount, move, blines, labels)
                aml_obj.create(trf_ml_vals)
                self._reconcile_payment_lines(blines)
                # consider entry_posted on account_journal
                if move.journal_id.entry_posted:
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
