# -*- coding: utf-8 -*-
# © 2009 EduSense BV (<http://www.edusense.nl>)
# © 2011-2013 Therp BV (<http://therp.nl>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
