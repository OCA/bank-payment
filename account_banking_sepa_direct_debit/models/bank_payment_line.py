# -*- coding: utf-8 -*-
##############################################################################
#
#    SEPA Direct Debit module for Odoo
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api


class BankPaymentLine(models.Model):
    _inherit = 'bank.payment.line'

    @api.multi
    def move_line_transfer_account_hashcode(self):
        """
        From my experience, even when you ask several direct debits
        at the same date with enough delay, you will have several credits
        on your bank statement: one for each mandate types.
        So we split the transfer move lines by mandate type, so easier
        reconciliation of the bank statement.
        """
        hashcode = super(BankPaymentLine, self).\
            move_line_transfer_account_hashcode()
        hashcode += '-' + unicode(self.mandate_id.recurrent_sequence_type)
        return hashcode
