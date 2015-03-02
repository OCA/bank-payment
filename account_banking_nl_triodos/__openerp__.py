##############################################################################
#
#    Copyright (C) 2009 - 2011 EduSense BV (<http://www.edusense.nl>)
#                              and Therp BV (<http://therp.nl>)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsability of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs
#    End users who are looking for a ready-to-use solution with commercial
#    garantees and support are strongly adviced to contract EduSense BV
#    or Therp BV
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
    'name': 'Triodos (NL) Bank Statements Import',
    'version': '0.168',
    'license': 'GPL-3',
    'author': "Therp BV / EduSense BV,Odoo Community Association (OCA)",
    'website': 'https://launchpad.net/account-banking',
    'category': 'Account Banking',
    'depends': ['account_banking'],
    'init_xml': [],
    'update_xml': [
        #'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'description': '''
Module to import Dutch Triodos bank format transation files (CSV format).

As the Triodos bank does not provide detailed specification concerning possible
values and their meaning for the fields in the CSV file format, the statements
are parsed according to an educated guess based on incomplete information.
You can contact the account-banking developers through their launchpad page and
help improve the performance of this import filter on
https://launchpad.net/account-banking.

Note that imported bank transfers are organized in statements covering periods
of one week, even if the imported files cover a different period.

This modules contains no logic, just an import filter for account_banking.
    ''',
    'active': False,
    'installable': True,
}
