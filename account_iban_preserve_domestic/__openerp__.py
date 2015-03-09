##############################################################################
#
#    Copyright (C) 2012 - 2013 Therp BV (<http://therp.nl>).
#
#    All other contributions are (C) by their respective contributors
#
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
    'name': 'Domestic bank account number',
    'version': '0.1.163',
    'license': 'AGPL-3',
    'author': "Therp BV,Odoo Community Association (OCA)",
    'website': 'https://launchpad.net/banking-addons',
    'category': 'Banking addons',
    'depends': [
        'base_iban',
        'account',
    ],
    'data': [
        'res_partner_bank_view.xml'
    ],
    'description': '''
This module is compatible with OpenERP 7.0.

The IBAN module in OpenERP 6.1/7.0 registers the IBAN
on the same field as the domestic account number,
instead of keeping both on separate fields as is the
case in 6.0.

This module adds a field to register the domestic account
number on IBANs, as the domestic account number is
still in use in certain regions. This should make for a
smoother migration to SEPA.
    ''',
    'active': False,
    'installable': True,
}
