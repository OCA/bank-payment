# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#              (C) 2011 - 2014 Therp BV (<http://therp.nl>).
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
    'name': 'Banking Addons - Iban lookup (legacy)',
    'version': '0.1',
    'license': 'AGPL-3',
    'author': "Banking addons community,Odoo Community Association (OCA)",
    'website': 'https://launchpad.net/banking-addons',
    'category': 'Banking addons',
    'depends': [
        'account_banking',
        'account_iban_preserve_domestic',
    ],
    'data': [
        'view/res_bank.xml',
        'view/res_partner_bank.xml',
    ],
    'external_dependencies': {
        'python': ['BeautifulSoup'],
    },
    'description': '''
This addons contains the legacy infrastructure for autocompletion of IBANs
and BBANs.

The autocompletion was implemented for Dutch IBANs, but as it turns out
the online database that it consults does not get updated. As a result,
the autocompletion will come up with outdated IBANs and BICs.

This module is deprecated and will be dropped in OpenERP 8.0.
    ''',
    'auto_install': False,
    'installable': True,
}
