# -*- coding: utf-8 -*-
# © 2015 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class BankPaymentLine(models.Model):
    _name = 'bank.payment.line'
    _description = 'Bank Payment Lines'

    name = fields.Char(string='Bank Payment Line Ref', required=True)
    order_id = fields.Many2one(
        'payment.order', string='Order', ondelete='cascade', select=True)
    payment_line_ids = fields.One2many(
        'payment.line', 'bank_line_id', string='Payment Lines')
    partner_id = fields.Many2one(
        'res.partner', string='Partner', related='payment_line_ids.partner_id')
    # Function Float fields are sometimes badly displayed in tree view,
    # see bug report https://github.com/odoo/odoo/issues/8632
    amount_currency = fields.Float(
        string='Amount', digits=dp.get_precision('Account'),
        compute='_compute_amount', store=True)
    # I would have preferred currency_id, but I need to keep the field names
    # similar to the field names of payment.line
    currency = fields.Many2one(
        'res.currency', string='Currency', required=True,
        related='payment_line_ids.currency')
    bank_id = fields.Many2one(
        'res.partner.bank', string='Bank Account',
        related='payment_line_ids.bank_id')
    date = fields.Date(
        string='Payment Date', related='payment_line_ids.date')
    state = fields.Selection(
        related='payment_line_ids.state', string='Communication Type')
    communication = fields.Char(string='Communication', required=True)
    company_id = fields.Many2one(
        'res.company', string='Company', readonly=True,
        related='order_id.company_id', store=True)

    @api.model
    def same_fields_payment_line_and_bank_payment_line(self):
        """
        This list of fields is used both to compute the grouping
        hashcode and to copy the values from payment line
        to bank payment line
        The fields must have the same name on the 2 objects
        """
        same_fields = [
            'currency', 'partner_id',
            'bank_id', 'date', 'state']
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
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'bank.payment.line')
        return super(BankPaymentLine, self).create(vals)
