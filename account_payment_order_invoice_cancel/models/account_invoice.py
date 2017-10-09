# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def action_cancel(self):
        invoices_with_payment_orders = self.\
            _get_invoice_linked_with_payment_orders()
        self = self - invoices_with_payment_orders
        res = True
        if self:
            res = super(AccountInvoice, self).action_cancel()
        if invoices_with_payment_orders:
            return invoices_with_payment_orders.\
                redirect_to_cancel_invoice_wizard()
        return res

    @api.multi
    def _get_invoice_linked_with_payment_orders(self):
        PaymentLineObj = self.env['account.payment.line']
        invoices = self.env['account.invoice']
        for rec in self:
            if not rec.move_id:
                continue
            payment_lines = PaymentLineObj.search([
                ('move_line_id.move_id', '=', rec.move_id.id),
            ])
            if payment_lines:
                invoices |= rec
        return invoices

    @api.multi
    def redirect_to_cancel_invoice_wizard(self):
        context = self.env.context.copy()
        context['active_ids'] = self.ids
        action = {
            'type': 'ir.actions.act_window',
            'name': _("Invoice cancel confirmation"),
            'res_model': 'account.payment.order.invoice_cancel',
            'view_mode': 'form',
            'target': 'new',
        }
        return action
