# -*- coding: utf-8 -*-
# Copyright 2017 Compassion CH (http://www.compassion.ch)
# @author: Marco Monzione <marco.mon@windowslive.com>, Emanuel Cino
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models, api


class AccountInvoiceFree(models.TransientModel):

    ''' Wizard to free invoices. When job is done, user is redirected on new
        payment order.
    '''
    _name = 'account.invoice.free'
    _description = 'Free invoice wizard'

    @api.multi
    def invoice_free(self):
        inv_obj = self.env['account.invoice']
        invoices = inv_obj.browse(self.env.context.get('active_ids'))
        return invoices.cancel_payment_lines()
