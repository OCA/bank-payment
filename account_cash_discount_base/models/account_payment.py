# -*- coding: utf-8 -*-
#
##############################################################################
#
#    Authors: Adrien Peiffer
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
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

from openerp import api, models, fields


class payment_line(models.Model):
    _inherit = 'payment.line'

    @api.one
    @api.depends('move_line_id')
    def _get_discount_due_date(self):
        if self.move_line_id and self.move_line_id.invoice:
            invoice = self.move_line_id.invoice
            self.discount_due_date = invoice.discount_due_date
        return

    discount_due_date = fields.Date(compute=_get_discount_due_date,
                                    string='Discount Due Date')
    discount_amount = fields.Float(string='Discount Amount', default=0.0)
    base_amount = fields.Float(string='Base Amount')

    @api.one
    @api.onchange('discount_amount')
    def discount_amount_change(self):
        self.amount_currency = self.base_amount - self.discount_amount
