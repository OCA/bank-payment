##############################################################################
#
#    Copyright (C) 2011 - 2013 Therp BV (<http://therp.nl>).
#    Copyright (C) 2011 Smile (<http://smile.fr>).
#    All Rights Reserved
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
{
    'name': 'Direct Debit',
    'version': '7.0.2.134',
    'license': 'AGPL-3',
    'author': 'Therp BV, Smile, Odoo Community Association (OCA)',
    'website': 'https://launchpad.net/banking-addons',
    'category': 'Banking addons',
    'depends': ['account_banking_payment_export'],
    'data': [
        'view/account_payment.xml',
        'view/account_invoice.xml',
        'view/payment_mode.xml',
        'view/payment_mode_type.xml',
        'workflow/account_invoice.xml',
        'data/account_payment_term.xml',
    ],
    'description': '''
This module adds support for direct debit orders, analogous to payment orders.
A new entry in the Accounting/Payment menu allow you to create a direct debit
order that helps you to select any customer invoices for you to collect.

This module explicitely implements direct debit orders as applicable
in the Netherlands. Debit orders are advanced in total by the bank.
Amounts that cannot be debited or are canceled by account owners are
credited afterwards. Such a creditation is called a storno. This style of
direct debit order may not apply to your country.

This module depends on and is part of the banking addons for OpenERP. This set
of modules helps you to provide support for communications with your local
banking institutions. The banking addons are a continuation of Account Banking
Framework by Edusense BV. See https://launchpad.net/banking-addons.
    ''',
    'installable': True,
}
