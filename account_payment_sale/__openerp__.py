# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account Payment Sale module for OpenERP
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
    'name': 'Account Payment Sale',
    'version': '1.0',
    'category': 'Banking addons',
    'license': 'AGPL-3',
    'summary': "Adds payment mode on sale orders",
    'description': """
Account Payment Sale
====================

This modules adds one field on sale orders: *Payment Mode*.
This field is copied from partner to sale order and then from sale order to
customer invoice.

This module is similar to the *sale_payment* module; the main difference is
that it doesn't depend on the *account_payment_extension* module (it's not the
only module to conflict with *account_payment_extension*; all the SEPA
modules in the banking addons conflict with *account_payment_extension*.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'contributors': ['Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>'],
    'depends': [
        'sale',
        'account_payment_partner'
    ],
    'conflicts': ['sale_payment'],
    'data': [
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'auto_install': True,
}
