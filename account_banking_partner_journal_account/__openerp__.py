##############################################################################
#
#    Copyright (C) 2013 Therp BV (<http://therp.nl>)
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
    'name': 'Banking Addons - Default partner journal accounts for bank'
            ' transactions',
    'version': '0.1',
    'license': 'AGPL-3',
    'author': "Therp BV,Odoo Community Association (OCA)",
    'website': 'https://launchpad.net/banking-addons',
    'category': 'Banking addons',
    'depends': ['account_banking'],
    'description': '''
This module allows to set alternative journal accounts on partners to use
as default accounts in imported bank statements.

This is useful when regular transactions on clearing accounts occur. Such
clearing accounts cannot usually be selected as default partner accounts
because they are neither of type 'payable' nor 'receivable' (or at least
never at the same time!). For the alternative journal accounts for bank
transactions, any reconcilable account can be selected.

When a transaction matches a specific move in the system, the account
from the move line takes still precedence so as not to impede
reconciliation.
    ''',
    'data': ['res_partner_view.xml'],
    'installable': True,
}
