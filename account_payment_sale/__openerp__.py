# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account Payment Sale module for OpenERP
#    Copyright (C) 2014 Akretion (http://www.akretion.com).
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
    'name': 'Account Payment Sale',
    'version': '8.0.1.0.0',
    'category': 'Banking addons',
    'license': 'AGPL-3',
    'summary': "Adds payment mode on sale orders",
    'author': "Akretion, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/bank-payment',
    'depends': [
        'sale',
        'account_payment_partner'
    ],
    'conflicts': ['sale_payment'],
    'data': [
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'auto_install': True,
}
