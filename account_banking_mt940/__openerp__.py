# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-2015 Therp BV <http://therp.nl>.
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
    'name': 'MT940',
    'version': '7.0.1.0.1',
    'license': 'AGPL-3',
    'author': 'Therp BV,Odoo Community Association (OCA)',
    'description': """
This addon provides a generic parser for MT940 files. Given that MT940 is a
non-open non-standard of pure evil in the way that every bank cooks up its own
interpretation of it, this addon alone won't help you much. It is rather
intended to be used by other addons to implement the dialect specific to a
certain bank.

See account_banking_nl_ing_mt940 for an example on how to use it.
    """,
    'category': 'Banking addons',
    'depends': [
        'account_banking',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
