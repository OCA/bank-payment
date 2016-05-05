# -*- coding: utf-8 -*-
# © 2015 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class BankPaymentLine(models.Model):
    _name = 'bank.payment.line'
    _description = 'Bank Payment Lines'

    name = fields.Char(
        string='Bank Payment Line Ref', required=True,
        readonly=True)
    order_id = fields.Many2one(
        'account.payment.order', string='Order', ondelete='cascade',
        select=True)
    payment_type = fields.Selection(
        related='order_id.payment_type', string="Payment Type",
        readonly=True, store=True)
    state = fields.Selection(
        related='order_id.state', string='State',
        readonly=True, store=True)
    payment_line_ids = fields.One2many(
        'account.payment.line', 'bank_line_id', string='Payment Lines',
        readonly=True)
    partner_id = fields.Many2one(
        'res.partner', related='payment_line_ids.partner_id',
        readonly=True)
    # Function Float fields are sometimes badly displayed in tree view,
    # see bug report https://github.com/odoo/odoo/issues/8632
    # But is it still true in v9 ?
    amount_currency = fields.Monetary(
        string='Amount', currency_field='currency_id',
        compute='_compute_amount', store=True, readonly=True)
    currency_id = fields.Many2one(
        'res.currency', required=True, readonly=True,
        related='payment_line_ids.currency_id')  # v8 field: currency
    partner_bank_id = fields.Many2one(
        'res.partner.bank', string='Bank Account', readonly=True,
        related='payment_line_ids.partner_bank_id')  # v8 field: bank_id
    date = fields.Date(
        related='payment_line_ids.date', readonly=True)
    communication_type = fields.Selection(
        related='payment_line_ids.communication_type', readonly=True)
    communication = fields.Char(
        string='Communication', required=True,
        readonly=True)  #, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one(
        related='order_id.payment_mode_id.company_id', store=True,
        readonly=True)
    # TODO : not shown in view ?
    # why on bank payment line and not on payment line ?
    transit_move_line_id = fields.Many2one(
        'account.move.line', string='Transfer Move Line', readonly=True,
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
                payment_type = bank_line.payment_type
                trf_lines = bank_line.transit_move_line_id.move_id.line_id
                for move_line in trf_lines:
                    if payment_type == 'inbound' and move_line.debit > 0:
                        bank_line.transfer_move_line_id = move_line
                    elif payment_type == 'outbound' and move_line.credit > 0:
                        bank_line.transfer_move_line_id = move_line

    @api.model
    def same_fields_payment_line_and_bank_payment_line(self):
        """
        This list of fields is used both to compute the grouping
        hashcode and to copy the values from payment line
        to bank payment line
        The fields must have the same name on the 2 objects
        """
        same_fields = [
            'currency_id', 'partner_id',
            'partner_bank_id', 'date', 'communication_type']
        return same_fields

    @api.multi
    @api.depends('payment_line_ids', 'payment_line_ids.amount_currency')
    def _compute_amount(self):
        for line in self:
            line.amount_currency = sum(
                line.mapped('payment_line_ids.amount_currency'))

    @api.model
    @api.returns('self')
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'bank.payment.line') or 'New'
        return super(BankPaymentLine, self).create(vals)

    @api.multi
    def move_line_transfer_account_hashcode(self):
        """
        This method is inherited in the module
        account_banking_sepa_direct_debit
        """
        self.ensure_one()
        if self.order_id.payment_mode_id.transfer_move_option == 'date':
            hashcode = self.date
        else:
            hashcode = unicode(self.id)
        return hashcode

