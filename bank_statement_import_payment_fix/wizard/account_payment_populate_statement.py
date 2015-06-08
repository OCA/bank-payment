# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Damien Crier
#    Copyright 2015 Camptocamp SA
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


class account_payment_populate_statement(models.TransientModel):
    _inherit = "account.payment.populate.statement"

    @api.model
    def _prepare_statement_line_vals(self, payment_line, amount, statement):
        """
        load amount_currency and currency_id from payment.line
        invert name and ref values
        """
        res = super(
            account_payment_populate_statement,
            self
            )._prepare_statement_line_vals(payment_line, amount, statement)

        res.update({
            'name': payment_line.communication,
            'ref': payment_line.order_id.reference or '?',
            'amount_currency': - payment_line.amount_currency or 0.0,
            'currency_id': payment_line.currency.id or False,
            })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
