##############################################################################
#
#    Copyright (C) 2011 Therp BV (<http://therp.nl>).
#                  2011 Smile BV (<http://smile.fr>).
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsability of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs
#    End users who are looking for a ready-to-use solution with commercial
#    garantees and support are strongly adviced to contract EduSense BV
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Account Payment Invoice Selection Shortcut',
    'version': '6.1.1.134',
    'license': 'GPL-3',
    'author': "Smile / Therp BV,Odoo Community Association (OCA)",
    'website': 'https://launchpad.net/banking-addons',
    'category': 'Banking addons',
    'depends': ['account_payment'],
    'init_xml': [],
    'update_xml': [
    ],
    'demo_xml': [],
    'description': '''
When composing a payment order, select all candidates by default (in the second step of the "Select invoices to pay" wizard).
    ''',
    'active': False,
    'installable': True,
}
