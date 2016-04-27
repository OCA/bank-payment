# -*- coding: utf-8 -*-
# © 2015 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
