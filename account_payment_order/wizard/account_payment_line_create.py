# -*- coding: utf-8 -*-
# © 2009 EduSense BV (<http://www.edusense.nl>)
# © 2011-2013 Therp BV (<http://therp.nl>)
# © 2014-2015 ACSONE SA/NV (<http://acsone.eu>)
# © 2015-2016 Akretion (<http://www.akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _


class AccountPaymentLineCreate(models.TransientModel):
    _name = 'account.payment.line.create'
    _description = 'Wizard to create payment lines'

    order_id = fields.Many2one(
        'account.payment.order', string='Payment Order')
    journal_ids = fields.Many2many(
        'account.journal', string='Journals Filter')
    invoice = fields.Boolean(
        string='Linked to an Invoice or Refund')
    date_type = fields.Selection([
        ('due', 'Due Date'),
        ('move', 'Move Date'),
        ], string="Type of Date Filter", required=True)
    due_date = fields.Date(string="Due Date")
    move_date = fields.Date(
        string='Move Date', default=fields.Date.context_today)
    payment_mode = fields.Selection([
        ('same', 'Same'),
        ('same_or_null', 'Same or Empty'),
        ('any', 'Any'),
        ], string='Payment Mode')
    move_line_ids = fields.Many2many(
        'account.move.line', string='Move Lines')

    @api.model
    def default_get(self, field_list):
        res = super(AccountPaymentLineCreate, self).default_get(field_list)
        context = self.env.context
        assert context.get('active_model') == 'account.payment.order',\
            'active_model should be payment.order'
        assert context.get('active_id'), 'Missing active_id in context !'
        order = self.env['account.payment.order'].browse(context['active_id'])
        mode = order.payment_mode_id
        res.update({
            'journal_ids': mode.default_journal_ids.ids or False,
            'invoice': mode.default_invoice,
            'date_type': mode.default_date_type,
            'payment_mode': mode.default_payment_mode,
            'order_id': order.id,
            })
        return res

    @api.multi
    def _prepare_move_line_domain(self):
        self.ensure_one()
        journals = self.journal_ids or self.env['account.journal'].search([])
        domain = [('move_id.state', '=', 'posted'),
                  ('reconciled', '=', False),
                  ('company_id', '=', self.order_id.company_id.id),
                  ('journal_id', 'in', journals.ids)]
        if self.date_type == 'due':
            domain += [
                '|',
                ('date_maturity', '<=', self.due_date),
                ('date_maturity', '=', False)]
        elif self.date_type == 'move':
            domain.append(('date', '<=', self.move_date))
        if self.invoice:
            domain.append(('invoice_id', '!=', False))
        if self.payment_mode:
            if self.payment_mode == 'same':
                domain.append(
                    ('payment_mode_id', '=', self.order_id.payment_mode_id.id))
            elif self.payment_mode == 'same_or_null':
                domain += [
                    '|',
                    ('payment_mode_id', '=', False),
                    ('payment_mode_id', '=', self.order_id.payment_mode_id.id)]

        if self.order_id.payment_type == 'outbound':
            # For payables, propose all unreconciled credit lines,
            # including partially reconciled ones.
            # If they are partially reconciled with a supplier refund,
            # the residual will be added to the payment order.
            #
            # For receivables, propose all unreconciled credit lines.
            # (ie customer refunds): they can be refunded with a payment.
            # Do not propose partially reconciled credit lines,
            # as they are deducted from a customer invoice, and
            # will not be refunded with a payment.
            domain += [
                ('credit', '>', 0),
                #'|',
                ('account_id.internal_type', '=', 'payable'),
                #'&',
                #('account_id.internal_type', '=', 'receivable'),
                #('reconcile_partial_id', '=', False),  # TODO uncomment
            ]
        elif self.order_id.payment_type == 'inbound':
            domain += [
                ('debit', '>', 0),
                ('account_id.internal_type', '=', 'receivable'),
                ]
        return domain

    @api.multi
    def populate(self):
        domain = self._prepare_move_line_domain()
        lines = self.env['account.move.line'].search(domain)
        self.move_line_ids = [(6, 0, lines.ids)]
        action = {
            'name': _('Select Move Lines to Create Transactions'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment.line.create',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': self._context,
        }
        return action

    @api.onchange(
        'date_type', 'move_date', 'due_date', 'journal_ids', 'invoice')
    def move_line_filters_change(self):
        domain = self._prepare_move_line_domain()
        res = {'domain': {'move_line_ids': domain}}
        return res

    @api.multi
    def filter_lines(self, lines):
        """ Filter move lines before proposing them for inclusion
            in the payment order.

        This implementation filters out move lines that are already
        included in draft or open payment orders. This prevents the
        user to include the same line in two different open payment
        orders. When the payment order is sent, it is assumed that
        the move will be reconciled soon (or immediately with
        account_banking_payment_transfer), so it will not be
        proposed anymore for payment.

        See also https://github.com/OCA/bank-payment/issues/93.

        :param lines: recordset of move lines
        :returns: list of move line ids
        """
        self.ensure_one()
        payment_lines = self.env['account.payment.line'].\
            search([('order_id.state', 'in', ('draft', 'open')),
                    ('move_line_id', 'in', lines.ids)])
        to_exclude = set([l.move_line_id.id for l in payment_lines])
        return [l.id for l in lines if l.id not in to_exclude]

    @api.multi
    def _prepare_payment_line(self, payment, line):
        """This function is designed to be inherited
        The resulting dict is passed to the create method of payment.line"""
        self.ensure_one()
        _today = fields.Date.context_today(self)
        date_to_pay = False  # no payment date => immediate payment
        if payment.date_prefered == 'due':
            # -- account_banking
            # date_to_pay = line.date_maturity
            date_to_pay = (
                line.date_maturity
                if line.date_maturity and line.date_maturity > _today
                else False)
            # -- end account banking
        elif payment.date_prefered == 'fixed':
            # -- account_banking
            # date_to_pay = payment.date_scheduled
            date_to_pay = (
                payment.date_scheduled
                if payment.date_scheduled and payment.date_scheduled > _today
                else False)
            # -- end account banking
        # -- account_banking
        state = 'normal'
        communication = line.ref or '-'
        if line.invoice:
            if line.invoice.reference_type == 'structured':
                state = 'structured'
                # Fallback to invoice number to keep previous behaviour
                communication = line.invoice.reference or line.invoice.number
            else:
                if line.invoice.type in ('in_invoice', 'in_refund'):
                    communication = (
                        line.invoice.reference or
                        line.invoice.supplier_invoice_number or line.ref)
                else:
                    # Make sure that the communication includes the
                    # customer invoice number (in the case of debit order)
                    communication = line.invoice.number
        # support debit orders when enabled
        if line.debit > 0:
            amount_currency = line.amount_residual_currency * -1
        else:
            amount_currency = line.amount_residual_currency
        if payment.payment_order_type == 'debit':
            amount_currency *= -1
        line2bank = line.line2bank(payment.mode.id)
        # -- end account banking
        res = {'move_line_id': line.id,
               'amount_currency': amount_currency,
               'bank_id': line2bank.get(line.id),
               'order_id': payment.id,
               'partner_id': line.partner_id and line.partner_id.id or False,
               # account banking
               'communication': communication,
               'state': state,
               # end account banking
               'date': date_to_pay,
               'currency': (line.invoice and line.invoice.currency_id.id or
                            line.journal_id.currency.id or
                            line.journal_id.company_id.currency_id.id)}
        return res

    @api.multi
    def create_payment_lines(self):
        if self.move_line_ids:
            self.move_line_ids.create_payment_line_from_move_line(
                self.order_id)
        return True
        # Force reload of payment order view as a workaround for lp:1155525
        return {'name': _('Payment Orders'),
                'context': context,
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_model': 'payment.order',
                'res_id': context['active_id'],
                'type': 'ir.actions.act_window'}
