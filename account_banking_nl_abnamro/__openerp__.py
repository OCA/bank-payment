# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 - 2011 EduSense BV (<http://www.edusense.nl>)
#                              and Therp BV (<http://therp.nl>)
#    All Rights Reserved
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
    'name': 'abnamro (NL) Bank Statements Import',
    'version': '0.1',
    'license': 'AGPL-3',
    'author': ['Therp BV', 'EduSense BV'],
    'website': 'https://launchpad.net/banking-addons',
    'category': 'Banking addons',
    'depends': ['account_banking'],
    'description': '''
Import filter for abnamro (NL) bank transaction files (txt/tab format).

No formal specifications of the file layout are released by abnamro. You can
help improve the performance of this import filter on
https://launchpad.net/account-banking.

Imported bank transfers are organized in statements covering periods of one
week, even if the imported files cover a different period.
''',
    'installable': False,
}
