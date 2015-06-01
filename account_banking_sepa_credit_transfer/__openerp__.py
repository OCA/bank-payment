# -*- encoding: utf-8 -*-
##############################################################################
#
#    SEPA Credit Transfer module for Odoo
#    Copyright (C) 2010-2015 Akretion (http://www.akretion.com)
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
    'name': 'Account Banking SEPA Credit Transfer',
    'summary': 'Create SEPA XML files for Credit Transfers',
    'version': '8.0.0.3.0',
    'license': 'AGPL-3',
    'author': "Akretion, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/bank-payment',
    'category': 'Banking addons',
    'depends': ['account_banking_pain_base'],
    'data': [
        'wizard/export_sepa_view.xml',
        'data/payment_type_sepa_sct.xml',
    ],
    'demo': [
        'demo/sepa_credit_transfer_demo.xml'
    ],
    'installable': True,
}
