# -*- encoding: utf-8 -*-
##############################################################################
#
#    French Letter of Change module for Odoo
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
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
    'name': 'French Letter of Change',
    'summary': 'Create French LCR CFONB files',
    'version': '0.1',
    'license': 'AGPL-3',
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com',
    'category': 'Banking addons',
    'depends': ['account_direct_debit'],
    'external_dependencies': {
        'python': ['unidecode'],
        },
    'data': [
        'account_banking_lcr_view.xml',
        'wizard/export_lcr_view.xml',
        'data/payment_type_lcr.xml',
        'security/ir.model.access.csv',
        ],
    'demo': ['lcr_demo.xml'],
    'installable': True,
}
