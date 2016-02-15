# -*- coding: utf-8 -*-
# © 2011 Smile (<http://smile.fr>)
# © 2011-2013 Therp BV (<http://therp.nl>)
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def line2bank(self, cr, uid, ids, payment_type=None, context=None):
        """I have to inherit this function for direct debits to fix the
        following issue : if the customer invoice has a value for
        'partner_bank_id', then it will take this partner_bank_id
        in the payment line... but, on a customer invoice,
        the partner_bank_id is the bank account of the company,
        not the bank account of the customer !
        """
        pay_mode_obj = self.pool['payment.mode']
        if payment_type:
            pay_mode = pay_mode_obj.browse(
                cr, uid, payment_type, context=context)
            if pay_mode.type.payment_order_type == 'debit':
                line2bank = {}
                bank_type = pay_mode_obj.suitable_bank_types(
                    cr, uid, pay_mode.id, context=context)
                for line in self.browse(cr, uid, ids, context=context):
                    line2bank[line.id] = False
                    if line.partner_id:
                        for bank in line.partner_id.bank_ids:
                            if bank.state in bank_type:
                                line2bank[line.id] = bank.id
                                break
                return line2bank
        return super(AccountMoveLine, self).line2bank(
            cr, uid, ids, payment_type=pay_mode.id, context=context)
