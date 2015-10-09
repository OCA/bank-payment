##############################################################################
#
#    Copyright (C) 2011 - 2013 Therp BV (<http://therp.nl>).
#    Copyright (C) 2011 Smile (<http://smile.fr>).
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': 'Direct Debit',
    'version': '8.0.2.0.0',
    'license': 'AGPL-3',
    'author': 'Therp BV, '
              'Smile, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/bank-payment',
    'category': 'Banking addons',
    'depends': ['account_banking_payment_export'],
    'data': [
        'views/account_payment.xml',
        'views/account_invoice.xml',
        'views/payment_mode.xml',
        'views/payment_mode_type.xml',
        'workflow/account_invoice.xml',
        'data/account_payment_term.xml',
        'data/payment_mode_type.xml'
    ],
    'installable': True,
}
