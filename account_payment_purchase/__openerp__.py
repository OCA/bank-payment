# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account Payment Purchase module for OpenERP
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
    'name': 'Account Payment Purchase',
    'version': '1.0',
    'category': 'Banking addons',
    'license': 'AGPL-3',
    'summary': "Adds Bank Account and Payment Mode on Purchase Orders",
    'description': """
Account Payment Purchase
========================

This modules adds 2 fields on purchase orders : *Bank Account* and *Payment
Mode*. These fields are copied from partner to purchase order and then from
purchase order to supplier invoice.

This module is similar to the *purchase_payment* module ; the main difference
is that it doesn't depend on the *account_payment_extension* module (it's not
the only module to conflict with *account_payment_extension* ; all the SEPA
modules in the banking addons conflict with *account_payment_extension*, cf
banking-addons-70/account_banking_payment_export/__openerp__.py).

Please contact Alexis de Lattre from Akretion <alexis.delattre@akretion.com>
for any help or question about this module.
    """,
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com',
    'depends': ['purchase', 'account_payment_partner'],
    'conflicts': ['purchase_payment'],
    'data': [
        'view/purchase.xml',
    ],
    'installable': True,
    'active': False,
}
