# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 Therp BV (<http://therp.nl>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

"""r64: introduction of the payment_mode_type in order to support of debit
orders
"""
__name__ = ("payment.mode.type:: set payment_mode_type to 'debit' for Clieop "
            "incasso export")


def migrate(cr, version):
    cr.execute("UPDATE payment_mode_type"
               " SET payment_order_type = 'debit'"
               " FROM ir_model_data "
               " WHERE res_id = payment_mode_type.id"
               " AND module = 'account_banking_nl_clieop'"
               " AND model = 'payment.mode.type'"
               " AND ir_model_data.name = 'export_clieop_inc'"
               )
