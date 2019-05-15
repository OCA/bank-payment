# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def get_payment_line_linked(self):
        payment_line_obj = self.env['account.payment.line']
        payment_lines = []
        if self.move_id.line_ids:
            inv_mv_lines = [x.id for x in self.move_id.line_ids]
            payment_lines = payment_line_obj \
                .search([('move_line_id', 'in', inv_mv_lines)])
        return payment_lines

    @api.multi
    def check_payment_line_linked(self):
        self.ensure_one()
        payment_lines = self.get_payment_line_linked()
        if payment_lines:
            return True
        else:
            return False

    @api.multi
    def action_invoice_cancel(self):
        for invoice in self:
            if invoice.check_payment_line_linked():
                return invoice.open_validate_invoice_cancel()
        return super(AccountInvoice, self).action_invoice_cancel()

    @api.multi
    def open_validate_invoice_cancel(self):
        self.ensure_one()
        wizard = self.env['validate.invoice.cancel'].create({
            'invoice_id': self.id,
        })
        return {
            'name': _("Validate Invoice Cancel"),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'validate.invoice.cancel',
            'res_id': wizard.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self.env.context
        }
