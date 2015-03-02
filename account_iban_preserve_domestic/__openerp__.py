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
    'name': 'Domestic bank account number',
    'version': '0.1.134',
    'license': 'AGPL-3',
    'author': "Therp BV,Odoo Community Association (OCA)",
    'website': 'https://launchpad.net/banking-addons',
    'category': 'Banking addons',
    'depends': ['base_iban','account'],
    'init_xml': [],
    'update_xml': [
        'res_partner_bank_view.xml'
        ],
    'demo_xml': [],
    'description': '''
This module is compatible with OpenERP 6.1.

The IBAN module in OpenERP 6.1 registers the IBAN
on the same field as the domestic account number, 
instead of keeping both on separate fields as is the
case in 6.0.

This module adds a field to register the domestic account
number on IBANs, while the domestic account number is
still widely in use in certain regions.

Note that an upgrade to OpenERP 6.1 makes you lose the
domestic account numbers on IBANs that were already in 
your system, unless you installed the 6.0 version of this
module prior to the upgrade to OpenERP 6.1. 
    ''',
    'active': False,
    'installable': True,
}
