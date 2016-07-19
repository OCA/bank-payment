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
    target_move = fields.Selection([
        ('posted', 'All Posted Entries'),
        ('all', 'All Entries'),
        ], string='Target Moves')
    allow_blocked = fields.Boolean(
        string='Allow Litigation Move Lines')
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
            'target_move': mode.default_target_move,
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
        domain = [('reconciled', '=', False),
                  ('company_id', '=', self.order_id.company_id.id),
                  ('journal_id', 'in', journals.ids)]
        if self.target_move == 'posted':
            domain += [('move_id.state', '=', 'posted')]
        if not self.allow_blocked:
            domain += [('blocked', '!=', True)]
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
                #  '|',
                ('account_id.internal_type', '=', 'payable'),
                #  '&',
                #  ('account_id.internal_type', '=', 'receivable'),
                #  ('reconcile_partial_id', '=', False),  # TODO uncomment
            ]
        elif self.order_id.payment_type == 'inbound':
            domain += [
                ('debit', '>', 0),
                ('account_id.internal_type', '=', 'receivable'),
                ]
        # Exclude lines that are already in a non-cancelled
        # and non-uploaded payment order; lines that are in a
        # uploaded payment order are proposed if they are not reconciled,
        paylines = self.env['account.payment.line'].search([
            ('state', 'in', ('draft', 'open', 'generated')),
            ('move_line_id', '!=', False)])
        if paylines:
            move_lines_ids = [payline.move_line_id.id for payline in paylines]
            domain += [('id', 'not in', move_lines_ids)]
        return domain

    @api.multi
    def populate(self):
        domain = self._prepare_move_line_domain()
        lines = self.env['account.move.line'].search(domain)
        self.move_line_ids = lines
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
        'date_type', 'move_date', 'due_date', 'journal_ids', 'invoice',
        'target_move', 'allow_blocked', 'payment_mode')
    def move_line_filters_change(self):
        domain = self._prepare_move_line_domain()
        res = {'domain': {'move_line_ids': domain}}
        return res

    @api.multi
    def create_payment_lines(self):
        if self.move_line_ids:
            self.move_line_ids.create_payment_line_from_move_line(
                self.order_id)
        return True
