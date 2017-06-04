# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
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
    "name": "Add payment mode to Account Invoice Report",
    "version": "1.0",
    "author": "Eficent",
    "website": "www.eficent.com",
    "category": "Accounting & Finance",
    "depends": ["account_payment_partner"],
    "init_xml": [],
    "update_xml": [
        "views/report_invoice.xml",
    ],
    'demo_xml': [

    ],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}