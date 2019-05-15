# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ValidateInvoiceCancel(models.TransientModel):

    _name = 'validate.invoice.cancel'

    invoice_id = fields.Many2one(
        'account.invoice',
        ondelete='cascade',
    )

    @api.multi
    def validate_cancel(self):
        payment_lines = self.invoice_id.get_payment_line_linked()
        payment_lines.write({'move_line_id': False})
        return self.invoice_id.action_invoice_cancel()
