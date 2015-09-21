# -*- encoding: utf-8 -*-
##############################################################################
#
#    PAIN Base module for Odoo
#    Copyright (C) 2013-2015 Akretion (http://www.akretion.com)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
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


class BankPaymentLine(models.Model):
    _inherit = 'bank.payment.line'

    priority = fields.Selection(
        related='payment_line_ids.priority', string='Priority')
    struct_communication_type = fields.Selection(
        related='payment_line_ids.struct_communication_type',
        string='Structured Communication Type')

    @api.model
    def same_fields_payment_line_and_bank_payment_line(self):
        res = super(BankPaymentLine, self).\
            same_fields_payment_line_and_bank_payment_line()
        res += ['priority', 'struct_communication_type']
        return res
