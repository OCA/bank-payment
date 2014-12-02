# -*- coding: utf-8 -*-
#
##############################################################################
#
#    Authors: Adrien Peiffer
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
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
    "name": "Account Cash Discount Base",
    "version": "1.0",
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    "images": [],
    "category": "Accounting",
    "depends": [
        "account_banking_payment_export",
    ],
    "description": """
    Account Cash Discount Base
""",
    "data": [
        'views/account_invoice_view.xml',
        'views/account_payment_view.xml',
        'wizard/account_payment_create_order_view.xml',
    ],
    "demo": [],
    "test": [],
    "licence": "AGPL-3",
    "installable": True,
    "auto_install": False,
    "application": True,
}
