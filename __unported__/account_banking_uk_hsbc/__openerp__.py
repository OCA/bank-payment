# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 credativ Ltd (<http://www.credativ.co.uk>).
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
    'name': 'HSBC Account Banking',
    'version': '0.5',
    'license': 'AGPL-3',
    'author': "credativ Ltd,Odoo Community Association (OCA)",
    'website': 'http://www.credativ.co.uk',
    'category': 'Account Banking',
    'depends': ['account_banking_payment'],
    'data': [
        'account_banking_uk_hsbc.xml',
        'hsbc_clientid_view.xml',
        'data/banking_export_hsbc.xml',
        'wizard/export_hsbc_view.xml',
        'security/ir.model.access.csv',
    ],
    'description': '''
Module to import HSBC format transation files (S.W.I.F.T MT940) and to export
payments for HSBC.net (PAYMUL).

Currently it is targetting UK market, due to country variances of the MT940 and
PAYMUL.

It is possible to extend this module to work with HSBC.net in other countries
and potentially other banks.

This module adds above import/export filter to the account_banking module.
All business logic is in account_banking module.

Initial release of this module was co-sponsored by Canonical.
''',
    'installable': False,
}
