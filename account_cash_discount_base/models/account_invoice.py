# -*- coding: utf-8 -*-
#
##############################################################################
#
#    Authors: Adrien Peiffer
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
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

from openerp import models, fields, api, exceptions, _
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    discount_percent = fields\
        .Float(string='Discount Percent', readonly=True,
               states={'draft': [('readonly', False)]})
    discount_amount = fields\
        .Float(string='Amount Discount deducted', readonly=True,
               states={'draft': [('readonly', False)]})
    discount = fields\
        .Float(compute='_compute_discount', string='Amount Discount',
               store=True)
    discount_delay = fields\
        .Integer(string='Discount Delay (days)', readonly=True,
                 states={'draft': [('readonly', False)]})
    discount_due_date = fields.Date(string='Discount Due Date', readonly=True,
                                    states={'draft': [('readonly', False)]})
    force_discount_amount = fields.Boolean(string="Force Discount Amount",
                                           states={'draft': [('readonly',
                                                              False)]})

    @api.depends('discount_amount')
    @api.one
    def _compute_discount(self):
        self.discount = self.amount_total - self.discount_amount

    @api.onchange('discount_delay')
    @api.one
    def _discount_delay_change(self):
        if self.discount != 0 and self.discount_delay != 0:
            if self.date_invoice:
                date_invoice = datetime.strptime(self.date_invoice,
                                                 DEFAULT_SERVER_DATE_FORMAT)
            else:
                date_invoice = datetime.now()
            due_date = date_invoice + timedelta(days=self.discount_delay)
            self.discount_due_date = due_date.date()

    @api.onchange('discount_percent', 'amount_tax', 'amount_total')
    @api.one
    def _change_discount_amount(self):
        if not self.force_discount_amount:
            discount_amount = 0.0
            if self.discount_percent == 0.0:
                discount_amount = self.amount_total
            else:
                discount = self.amount_untaxed * \
                    (0.0 + self.discount_percent/100)
                discount_amount = (self.amount_total - discount)
            self.discount_amount = discount_amount

    @api.multi
    def action_move_create(self):
        super(account_invoice, self).action_move_create()
        for inv in self:
            inv._discount_delay_change()
            if not inv.discount_due_date and inv.discount != 0.0:
                raise exceptions.Warning(_('Warning !\n You have to define '
                                           'a discount due date'))
        return True
