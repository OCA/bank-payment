# -*- coding: utf-8 -*-
# © 2015-2016 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class BankPaymentLine(models.Model):
    _inherit = 'bank.payment.line'

    @api.multi
    def move_line_offsetting_account_hashcode(self):
        """
        From my experience, even when you ask several direct debits
        at the same date with enough delay, you will have several credits
        on your bank statement: one for each mandate types.
        So we split the transfer move lines by mandate type, so easier
        reconciliation of the bank statement.
        """
        hashcode = super(BankPaymentLine, self).\
            move_line_offsetting_account_hashcode()
        hashcode += '-' + unicode(self.mandate_id.recurrent_sequence_type)
        return hashcode
