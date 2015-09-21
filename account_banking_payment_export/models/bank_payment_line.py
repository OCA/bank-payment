# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
        compute='_compute_amount')
    # I would have prefered currency_id, but I need to keep the field names
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

    @api.one
    @api.depends('payment_line_ids.amount_currency')
    def _compute_amount(self):
        amount = 0.0
        for payline in self.payment_line_ids:
            amount += payline.amount_currency
        self.amount_currency = amount

    @api.model
    @api.returns('self')
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'bank.payment.line')
        return super(BankPaymentLine, self).create(vals)
