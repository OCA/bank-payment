# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#              (C) 2011 - 2013 Therp BV (<http://therp.nl>).
#            
#    All other contributions are (C) by their respective contributors
#
#    All Rights Reserved
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
    'name': 'Account Banking - Payments',
    'version': '0.1.164',
    'license': 'AGPL-3',
    'author': 'Banking addons community',
    'website': 'https://launchpad.net/banking-addons',
    'category': 'Banking addons',
    'depends': [
        'account_payment',
        ],
    'data': [
        'view/account_payment.xml',
        'view/bank_payment_manual.xml',
        'view/payment_mode.xml',
        'view/payment_mode_type.xml',
        'data/payment_mode_type.xml',
        'security/ir.model.access.csv',
    ],
    'description': '''
    This addon adds payment export infrastructure to the Banking Addons.
    * the "make payment" launches a wizard depending on the payment mode
    * create a manual payment mode type
    * various improvements to the payment order invoice import wizard
    * suitable bank account type filtering
    ''',
    'auto_install': True,
    'installable': True,
}
