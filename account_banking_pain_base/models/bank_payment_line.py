# -*- coding: utf-8 -*-
# © 2013-2015 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
