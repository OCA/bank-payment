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

from openerp import models, fields, api
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    discount_percent = fields.Float(string='Discount Percent')
    discount_amount = fields.Float(string='Amount Discount included')
    discount_delay = fields.Integer(string='Discount Delay (days)')
    discount_due_date = fields.Date(string='Discount Due Date')

    @api.one
    @api.onchange('discount_percent')
    def change_discount_percent(self):
        self.discount_amount = self._compute_discount_amount(self)
        return

    @api.one
    @api.onchange('amount_untaxed')
    def change_untaxed_amount(self):
        self.discount_amount = self._compute_discount_amount(self)
        return

    @api.v8
    def _compute_discount_amount(self, invoice):
        discount = invoice.amount_untaxed * (0.0 + invoice
                                             .discount_percent/100)
        return (invoice.amount_total - discount)

    @api.v8
    def _compute_discount_due_date(self, date_invoice, discount_delay):
        if date_invoice:
            date_invoice = datetime.strptime(date_invoice,
                                             DEFAULT_SERVER_DATE_FORMAT)
        else:
            date_invoice = datetime.now()
        due_date = date_invoice + timedelta(days=discount_delay)
        discount_due_date = due_date.date()
        return discount_due_date

    @api.one
    @api.onchange('discount_delay')
    def discount_delay_change(self):
        discount_due_date = self\
            ._compute_discount_due_date(self.date_invoice, self.discount_delay)
        self.discount_due_date = discount_due_date
        return
