# -*- coding: utf-8 -*-
# Copyright 2017 Compassion CH (http://www.compassion.ch)
# @author: Marco Monzione <marco.mon@windowslive.com>, Emanuel Cino
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models, api, _, exceptions


class AccountInvoice(models.Model):

    """ Inherit invoice to add invoice freeing functionality. It's about
        cancelling related payment line. This
        way, the invoice (properly, invoice's move lines) can be used again
        in another payment order.
    """
    _inherit = 'account.invoice'

    @api.multi
    def cancel_payment_lines(self):
        """ This function simply finds related payment lines and cancel them.
        """
        mov_line_obj = self.env['account.move.line']
        pay_line_obj = self.env['account.payment.line']
        move_ids = self.mapped('move_id.id')
        move_line_ids = mov_line_obj.search([('move_id', 'in', move_ids)]).ids
        payment_lines = pay_line_obj.search([
            ('move_line_id', 'in', move_line_ids)
        ])
        if not payment_lines:
            raise exceptions.UserError(_('No payment line found !'))

        payment_lines.cancel_line()
