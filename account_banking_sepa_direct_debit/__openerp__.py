# -*- encoding: utf-8 -*-
##############################################################################
#
#    SEPA Direct Debit module for OpenERP
#    Copyright (C) 2013 Akretion (http://www.akretion.com)
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
    'version': '0.1',
    'license': 'AGPL-3',
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com',
    'contributors': ['Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>'],
    'category': 'Banking addons',
    'depends': [
        'account_direct_debit',
        'account_banking_pain_base',
        'account_banking_mandate',
    ],
    'external_dependencies': {
        'python': ['unidecode', 'lxml'],
    },
    'data': [
        'views/account_banking_sdd_view.xml',
        'views/account_banking_mandate_view.xml',
        'views/res_company_view.xml',
        'wizard/export_sdd_view.xml',
        'data/mandate_expire_cron.xml',
        'data/payment_type_sdd.xml',
        'security/original_mandate_required_security.xml',
        'security/ir.model.access.csv',
    ],
    'demo': ['demo/sepa_direct_debit_demo.xml'],
    'description': '''
Module to export direct debit payment orders in SEPA XML file format.

SEPA PAIN (PAyment INitiation) is the new european standard for
Customer-to-Bank payment instructions. This module implements SEPA Direct
Debit (SDD), more specifically PAIN versions 008.001.02, 008.001.03 and
008.001.04. It is part of the ISO 20022 standard, available on
http://www.iso20022.org.

The Implementation Guidelines for SEPA Direct Debit published by the European
Payments Council (http://http://www.europeanpaymentscouncil.eu) use PAIN
version 008.001.02. So if you don't know which version your bank supports, you
should try version 008.001.02 first.
    ''',
    'installable': True,
}
