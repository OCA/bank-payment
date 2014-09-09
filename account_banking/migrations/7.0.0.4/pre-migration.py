# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Akretion (http://www.akretion.com/)
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


def table_exists(cr, table):
    """ Check whether a certain table or view exists """
    cr.execute(
        'SELECT count(relname) FROM pg_class WHERE relname = %s',
        (table,))
    return cr.fetchone()[0] == 1


def migrate(cr, version):
    """
    Migration script for semantic changes in account_banking_payment_export.
    Putting the same script in this module for users migrating from 6.1,
    before the export module was refactored out.
    """
    if not version or not table_exists(cr, 'payment_line'):
        return
    cr.execute(
        "UPDATE payment_line SET communication = communication2, "
        "communication2 = null "
        "FROM payment_order "
        "WHERE payment_line.order_id = payment_order.id "
        "AND payment_order.state in ('draft', 'open') "
        "AND payment_line.state = 'normal' "
        "AND communication2 is not null")
