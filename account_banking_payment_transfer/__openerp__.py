# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#              (C) 2011 - 2013 Therp BV (<http://therp.nl>).
#              (C) 2014 ACSONE SA/NV (<http://acsone.eu>).
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
    'name': 'Account Banking - Payments Transfer Account',
    'version': '8.0.0.2.0',
    'license': 'AGPL-3',
    'author': "Banking addons community,Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/banking',
    'category': 'Banking addons',
    'post_init_hook': 'set_date_sent',
    'depends': [
        'account_banking_payment_export',
    ],
    'data': [
        'view/payment_mode.xml',
        'workflow/account_payment.xml',
        'view/account_payment.xml',
    ],
    'test': [
        'test/data.yml',
        'test/test_payment_method.yml',
        'test/test_partial_payment_refunded.yml',
        'test/test_partial_payment_transfer.yml',


    ],
    'auto_install': False,
    'installable': True,
}
