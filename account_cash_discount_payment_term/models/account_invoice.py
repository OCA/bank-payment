# -*- coding: utf-8 -*-
#
##############################################################################
#
#    Authors: Adrien Peiffer
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
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

from openerp import api, models


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def onchange_payment_term_date_invoice(self, payment_term_id,
                                           date_invoice):
        res = super(account_invoice, self)\
            .onchange_payment_term_date_invoice(payment_term_id, date_invoice)
        pterm = self.env['account.payment.term'].browse(payment_term_id)
        self = len(self.ids) > 0 and self[0] or self
        if self.type in ['in_invoice', 'out_invoice']:
            res['value']['discount_percent'] =\
                pterm.discount_percent
            res['value']['discount_delay'] = pterm.discount_delay
        return res
