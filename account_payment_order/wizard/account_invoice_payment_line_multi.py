# -*- coding: utf-8 -*-
# © 2016 Akretion (<http://www.akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class AccountInvoicePaymentLineMulti(models.TransientModel):
    _name = 'account.invoice.payment.line.multi'
    _description = 'Create payment lines from invoice tree view'

    @api.multi
    def run(self):
        self.ensure_one()
        assert self._context['active_model'] == 'account.invoice',\
            'Active model should be account.invoice'
        invoices = self.env['account.invoice'].browse(
            self._context['active_ids'])
        action = invoices.create_account_payment_line()
        return action
