# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Therp BV (<http://therp.nl>)
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
    'name': 'Banking Addons - Tests',
    'version': '8.0.0.1.0',
    'license': 'AGPL-3',
    'author': "Therp BV,Odoo Community Association (OCA)",
    'website': 'https://launchpad.net/banking-addons',
    'category': 'Banking addons',
    'depends': [
        'account_accountant',
        'account_banking_payment_transfer',
        'account_banking_sepa_credit_transfer',
        ],
    'description': '''
This addon adds unit tests for the Banking addons. Installing this
module will not give you any benefit other than having the tests'
dependencies installed, so that you can run the tests. If you only
run the tests manually, you don't even have to install this module,
only its dependencies.
    ''',
    'installable': True,
}
