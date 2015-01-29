# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Pexego (<http://www.pexego.es>).
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
    'name': 'Invoice bank usability',
    'version': '0.1',
    'license': 'AGPL-3',
    'author': 'Banking addons community',
    'website': 'https://github.com/OCA/banking',
    'category': 'Banking addons',
    'depends': ['account'],
    'data': ['views/account_invoice_view.xml'],
    'description': '''Allow to select customer bank accounts on customer
    invoices.''',
    'auto_install': False,
    'installable': True,
}
