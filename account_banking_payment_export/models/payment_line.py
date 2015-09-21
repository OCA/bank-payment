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


class PaymentLine(models.Model):
    _inherit = 'payment.line'

    bank_line_id = fields.Many2one(
        'bank.payment.line', string='Bank Payment Line')

    @api.multi
    def payment_line_hashcode(self):
        self.ensure_one()
        bplo = self.env['bank.payment.line']
        values = []
        for field in bplo.same_fields_payment_line_and_bank_payment_line():
            values.append(unicode(self[field]))
        hashcode = '-'.join(values)
        return hashcode
