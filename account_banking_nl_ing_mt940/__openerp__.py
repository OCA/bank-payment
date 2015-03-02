# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
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
    "name" : "MT940 import for Dutch ING",
    "version" : "1.0",
    "author" : "Therp BV,Odoo Community Association (OCA)",
    "complexity": "normal",
    "description": """
This addon imports the structured MT940 format as offered by the Dutch ING
bank.
    """,
    "category" : "Account Banking",
    "depends" : [
        'account_banking_mt940',
    ],
    "data" : [
    ],
    "js": [
    ],
    "css": [
    ],
    "qweb": [
    ],
    "auto_install": False,
    "installable": True,
    "application": False,
    "external_dependencies" : {
        'python' : [],
    },
}
