##############################################################################
#
#    Copyright (C) 2012 Therp BV (<http://therp.nl>).
#            
#    All other contributions are (C) by their respective contributors
#
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
    'name': 'Preserve domestic bank account number',
    'version': '0.1',
    'license': 'GPL-3',
    'author': 'Therp BV',
    'website': 'https://launchpad.net/banking-addons',
    'category': 'Banking addons',
    'depends': ['base_iban'],
    'init_xml': [],
    'update_xml': [],
    'demo_xml': [],
    'description': '''
This module is compatible with OpenERP 6.0.

The IBAN module in OpenERP 6.1 registers the IBAN
on the same field as the domestic account number, 
instead of keeping both on separate fields as is the
case in 6.0. That means that an upgrade to OpenERP 6.1
makes you lose this information. If you want to keep
the domestic account number in addition to the IBAN,
install this module prior to the upgrade to OpenERP 6.1. 

Do *not* install this version of the module on OpenERP 6.1.
A dedicated module for OpenERP 6.1 will be available that
allows you to access the domestic account number.
    ''',
    'active': False,
    'installable': True,
}
