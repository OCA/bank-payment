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

""" This script covers the migration of the payment wizards from old style to
new style (osv_memory). It guarantees an easy upgrade for early adopters
of the 6.0 branch of this OpenERP module. Note that a migration from OpenERP
5.0 to OpenERP 6.0 with respect to this module is not covered by this script.
"""

__name__ = ("payment.mode.type:: Add new style payment wizards to existing "
            "payment mode types")


def migrate(cr, version):
    cr.execute("UPDATE payment_mode_type"
               " SET ir_model_id = data1.res_id"
               " FROM ir_model_data data1,"
               "      ir_model_data data2"
               " WHERE data2.res_id = payment_mode_type.id"
               " AND data1.module = 'account_banking_nl_clieop'"
               " AND data1.model = 'ir.model'"
               " AND data1.name = 'model_banking_export_clieop_wizard'"
               " AND data2.module = 'account_banking_nl_clieop'"
               " AND data2.model = 'payment.mode.type'"
               " AND data2.name IN ('export_clieop_inc',"
               "                    'export_clieop_pay',"
               "                    'export_clieop_sal'"
               "                   )"
               )
