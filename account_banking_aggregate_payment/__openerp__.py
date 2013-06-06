# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>).
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
    'name': 'Account Banking Aggregate Payment',
    'version': '0.1.136',
    'license': 'GPL-3',
    'author': 'Therp BV',
    'website': 'https://launchpad.net/banking-addons',
    'category': 'Banking addons',
    'depends': ['account_banking'],
    'data': [
        'view/payment_mode.xml',
        'view/export_aggregate.xml',
        'data/payment_mode_type.xml',
        ],
    },
    'description': '''
    Allows for aggregating several payments on a single partner by
    reconciling the payment lines in a payment order of this type
    with a single line on the partner, then proceeds to create a new
    order of a user chosen type with only this line in it.
    ''',
    'active': False,
}
