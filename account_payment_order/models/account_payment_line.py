# -*- coding: utf-8 -*-
# © 2015-2016 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import UserError


class AccountPaymentLine(models.Model):
    _name = 'account.payment.line'
    _description = 'Payment Lines'

    name = fields.Char(string='Payment Reference', readonly=True, copy=False)
    order_id = fields.Many2one(
        'account.payment.order', string='Payment Order',
        ondelete='cascade', select=True)
    company_id = fields.Many2one(
        related='order_id.company_id', store=True, readonly=True)
    company_currency_id = fields.Many2one(
        related='order_id.company_currency_id', store=True, readonly=True)
    payment_type = fields.Selection(
        related='order_id.payment_type', store=True, readonly=True)
    bank_account_required = fields.Boolean(
        related='order_id.payment_method_id.bank_account_required',
        readonly=True)
    state = fields.Selection(
        related='order_id.state', string='State',
        readonly=True, store=True)
    move_line_id = fields.Many2one(
        'account.move.line', string='Journal Item',
        ondelete='restrict')
    ml_maturity_date = fields.Date(
        related='move_line_id.date_maturity', readonly=True)
    currency_id = fields.Many2one(
        'res.currency', string='Currency of the Payment Transaction',
        required=True,
        default=lambda self: self.env.user.company_id.currency_id)
    # v8 field : currency
    amount_currency = fields.Monetary(
        string="Amount", currency_field='currency_id')
    amount_company_currency = fields.Monetary(
        compute='compute_amount_company_currency',
        string='Amount in Company Currency', readonly=True,
        currency_field='company_currency_id')  # v8 field : amount
    partner_id = fields.Many2one(
        'res.partner', string='Partner', required=True,
        domain=[('parent_id', '=', False)])
    partner_bank_id = fields.Many2one(
        'res.partner.bank', string='Partner Bank Account', required=False,
        ondelete='restrict')  # v8 field : bank_id
    date = fields.Date(string='Payment Date')
    communication = fields.Char(
        string='Communication', required=True,
        help="Label of the payment that will be seen by the destinee")
    communication_type = fields.Selection([
        ('normal', 'Free'),
        ], string='Communication Type', required=True, default='normal')
    # v8 field : state
    bank_line_id = fields.Many2one(
        'bank.payment.line', string='Bank Payment Line', readonly=True)

    _sql_constraints = [(
        'name_company_unique',
        'unique(name, company_id)',
        'A payment line already exists with this reference '
        'in the same company!'
        )]

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'account.payment.line') or 'New'
        return super(AccountPaymentLine, self).create(vals)

    @api.multi
    @api.depends(
        'amount_currency', 'currency_id', 'company_currency_id', 'date')
    def compute_amount_company_currency(self):
        for line in self:
            if line.currency_id and line.company_currency_id:
                line.amount_company_currency = line.currency_id.with_context(
                    date=line.date).compute(
                        line.amount_currency, line.company_currency_id)

    @api.multi
    def payment_line_hashcode(self):
        self.ensure_one()
        bplo = self.env['bank.payment.line']
        values = []
        for field in bplo.same_fields_payment_line_and_bank_payment_line():
            values.append(unicode(self[field]))
        # Don't group the payment lines that are attached to the same supplier
        # but to move lines with different accounts (very unlikely),
        # for easier generation/comprehension of the transfer move
        values.append(unicode(self.move_line_id.account_id or False))
        # Don't group the payment lines that use a structured communication
        # otherwise it would break the structured communication system !
        if self.communication_type != 'normal':
            values.append(unicode(self.id))
        hashcode = '-'.join(values)
        return hashcode

    @api.onchange('partner_id')
    def partner_id_change(self):
        partner_bank = False
        if self.partner_id.bank_ids:
            partner_bank = self.partner_id.bank_ids[0]
        self.partner_bank_id = partner_bank

    @api.onchange('move_line_id')
    def move_line_id_change(self):
        if self.move_line_id:
            vals = self.move_line_id._prepare_payment_line_vals(self.order_id)
            vals.pop('order_id')
            for field, value in vals.iteritems():
                self[field] = value
        else:
            self.partner_id = False
            self.partner_bank_id = False
            self.amount_currency = 0.0
            self.currency_id = False
            self.communication = False

    def invoice_reference_type2communication_type(self):
        """This method is designed to be inherited by
        localization modules"""
        # key = value of 'reference_type' field on account_invoice
        # value = value of 'communication_type' field on account_payment_line
        res = {'none': 'normal'}
        return res

    @api.multi
    def draft2open_payment_line_check(self):
        self.ensure_one()
        if self.bank_account_required and not self.partner_bank_id:
            raise UserError(_(
                'Missing Partner Bank Account on payment line %s') % self.name)
