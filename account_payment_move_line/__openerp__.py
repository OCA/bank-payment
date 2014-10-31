# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account Payment Move Line module for OpenERP
#    Copyright (C) 2014 KMEE (http://www.kmee.com.br)
#    @author Luis Felipe Miléo <mileo@kmee.com.br>
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
    'name': 'Account Payment Move Line',
    'version': '0.1',
    'category': 'Banking addons',
    'license': 'AGPL-3',
    'summary': 'Adds payment mode on move lines',
    'description': """
Account Move Line
=======================

This module adds the payment mode field in account move line

* the *Payment Mode* from Invoices is copied when the move lines are created.
""",
    'author': 'KMEE',
    'website': 'http://www.kmee.com.br',
    'depends': ['account_payment_partner'],
    'data': [
        'view/account_move_line.xml',
    ],
    'demo': [
    ],
    'active': False,
}
