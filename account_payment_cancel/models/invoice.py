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
from odoo import models, api, _, exceptions


class AccountInvoice(models.Model):

    ''' Inherit invoice to add invoice freeing functionality. It's about
        moving related payment line in a new cancelled payment order. This
        way, the invoice (properly, invoice's move lines) can be used again
        in another payment order.
    '''
    _inherit = 'account.invoice'

    @api.multi
    def cancel_payment_lines(self):
        ''' This function simply finds related payment lines and move them
            in a new payment order.
        '''
        mov_line_obj = self.env['account.move.line']
        pay_line_obj = self.env['account.payment.line']
        account_payment_cancel = self.env['account.payment.cancel']

        move_ids = self.mapped('move_id.id')

        move_line_ids = mov_line_obj.search([('move_id', 'in', move_ids)]).ids
        payment_lines = pay_line_obj.search([
            ('move_line_id', 'in', move_line_ids)
        ])

        if not payment_lines:
            raise exceptions.UserError(_('No payment line found !'))

        bank_payment_lines = payment_lines.mapped('bank_line_id')
        # It should have only one payment order
        old_pay_order = payment_lines.mapped('order_id')

        for bank_payment_line in bank_payment_lines:
            account_payment_cancel.cancel_payment(old_pay_order,
                                                  bank_payment_line,
                                                  None)
