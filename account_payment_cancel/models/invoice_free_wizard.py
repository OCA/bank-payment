# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Marco Monzione <marco.mon@windowslive.com>, Emanuel Cino
#
#    The licence is in the file __manifest__.py
#
##############################################################################
from odoo import models, api


class AccountInvoiceFree(models.TransientModel):

    ''' Wizard to free invoices. When job is done, user is redirected on new
        payment order.
    '''
    _name = 'account.invoice.free'

    @api.multi
    def invoice_free(self):
        inv_obj = self.env['account.invoice']
        invoices = inv_obj.browse(self.env.context.get('active_ids'))
        return invoices.cancel_payment_lines()
