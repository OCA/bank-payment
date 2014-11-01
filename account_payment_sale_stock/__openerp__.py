# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account Payment Sale Stock module for OpenERP
#    Copyright (C) 2014 Akretion (http://www.akretion.com).
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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

{
    'name': 'Account Payment Sale Stock',
    'version': '1.0',
    'category': 'Banking addons',
    'license': 'AGPL-3',
    'summary': "Manage payment mode when invoicing a sale from picking",
    'description': """
Account Payment Sale Stock
==========================

This module copies *Payment Mode* from sale order to invoice when it is
generated from the picking.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'contributors': ['Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>'],
    'depends': ['sale_stock',
                'account_payment_sale'],
    'conflicts': ['account_payment_extension'],
    'auto_install': True,
    'installable': True,
}
