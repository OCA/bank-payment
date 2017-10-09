# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountPaymentOrderInvoiceCancel(models.TransientModel):

    _name = 'account.payment.order.invoice_cancel'

    invoice_ids = fields.Many2many(
        comodel_name='account.invoice',
        relation='payment_order_invoice_rel',
        column1='wizard_po_invoice_cancel_id', column2='invoice_id',
    )

    @api.model
    def default_get(self, fields_list):
        res = super(
            AccountPaymentOrderInvoiceCancel, self).default_get(fields_list)
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            res['invoice_ids'] = [(6, 0, active_ids)]
        return res

    @api.multi
    def doit(self):
        self.ensure_one()
        invoices = self.invoice_ids
        move_ids = invoices.mapped('move_id').ids
        payment_lines = self.env['account.payment.line'].search([
            ('move_line_id.move_id', 'in', move_ids),
        ])
        payment_lines.write({'move_line_id': False})
        invoices.action_cancel()
        return True
