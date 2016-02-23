# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP - Sepa identifier suffixes per payment mode
#    Copyright (C) 2016 Comunitea Servicios Tecnológicos.
#    Omar Castiñeira Saavedra - omar@comunitea.com
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
    "name": "Account Banking Sepa - Sepa identifier suffixes per payment mode",
    "version": "8.0.0.0.0",
    "author": "Comunitea,Odoo Community Association (OCA)",
    "website": "http://www.comunitea.com",
    "category": "Banking addons",
    "description": """
- This addon allows to change sepa identifiers suffixes from payment modes.
    """,
    "depends": [
        "account_banking_pain_base"
    ],
    "demo": [],
    "data": [
        "views/payment_mode_view.xml"
    ],
    "installable": True,
}
