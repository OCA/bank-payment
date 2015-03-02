##############################################################################
#
#    Copyright (C) 2011 Therp BV (<http://therp.nl>).
#                  2011 Smile BV (<http://smile.fr>).
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
    'name': 'Account Payment Invoice Selection Shortcut',
    'version': '1.134',
    'license': 'AGPL-3',
    'author': "Smile / Therp BV,Odoo Community Association (OCA)",
    'website': 'https://launchpad.net/banking-addons',
    'category': 'Banking addons',
    'depends': ['account_payment'],
    'description': '''
When composing a payment order, select all candidates by default
(in the second step of the "Select invoices to pay" wizard).
    ''',
    'installable': True,
}
