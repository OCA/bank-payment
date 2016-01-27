# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#              (C) 2011 - 2013 Therp BV (<http://therp.nl>).
#
#    All other contributions are (C) by their respective contributors
#
#    All Rights Reserved
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

from openerp import models, fields, api


class PaymentLine(models.Model):
    '''
    Add some fields; make destination bank account
    mandatory, as it makes no sense to send payments into thin air.
    Edit: Payments can be by cash too, which is prohibited by mandatory bank
    accounts.
    '''
    _inherit = 'payment.line'

    msg = fields.Char('Message', required=False, readonly=True, default='')
    date_done = fields.Date('Date Confirmed', select=True, readonly=True)

    @api.multi
    def payment_line_hashcode(self):
        """
        Don't group the payment lines that are attached to the same supplier
        but to move lines with different accounts (very unlikely),
        for easier generation/comprehension of the transfer move
        """
        res = super(PaymentLine, self).payment_line_hashcode()
        res += '-' + unicode(
            self.move_line_id and self.move_line_id.account_id or False)
        return res
