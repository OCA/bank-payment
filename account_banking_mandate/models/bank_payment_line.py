# -*- encoding: utf-8 -*-
##############################################################################
#
#    Mandate module for Odoo
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
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

    mandate_id = fields.Many2one(
        comodel_name='account.banking.mandate', string='Direct Debit Mandate',
        related='payment_line_ids.mandate_id')

    @api.model
    def same_fields_payment_line_and_bank_payment_line(self):
        res = super(BankPaymentLine, self).\
            same_fields_payment_line_and_bank_payment_line()
        res.append('mandate_id')
        return res
