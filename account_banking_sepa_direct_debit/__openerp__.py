# -*- encoding: utf-8 -*-
##############################################################################
#
#    SEPA Direct Debit module for Odoo
#    Copyright (C) 2013-2015 Akretion (http://www.akretion.com)
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
    'name': 'Account Banking SEPA Direct Debit',
    'summary': 'Create SEPA files for Direct Debit',
    'version': '8.0.0.2.0',
    'license': 'AGPL-3',
    'author': "Akretion, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/bank-payment',
    'category': 'Banking addons',
    'depends': [
        'account_direct_debit',
        'account_banking_pain_base',
        'account_banking_mandate',
    ],
    'data': [
        'views/account_banking_mandate_view.xml',
        'views/res_company_view.xml',
        'wizard/export_sdd_view.xml',
        'data/mandate_expire_cron.xml',
        'data/payment_type_sdd.xml',
        'security/original_mandate_required_security.xml',
    ],
    'demo': ['demo/sepa_direct_debit_demo.xml'],
    'installable': True,
}
