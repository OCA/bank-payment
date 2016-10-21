# -*- coding: utf-8 -*-
# © 2011 Smile (<http://smile.fr>)
# © 2011-2013 Therp BV (<http://therp.nl>)
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Direct Debit',
    'version': '8.0.2.1.0',
    'license': 'AGPL-3',
    'author': 'Therp BV, '
              'Smile, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/bank-payment',
    'category': 'Banking addons',
    'depends': ['account_banking_payment_export'],
    'data': [
        'views/account_payment.xml',
        'views/payment_mode.xml',
        'views/payment_mode_type.xml',
        'data/account_payment_term.xml',
        'data/payment_mode_type.xml'
    ],
    'installable': True,
}
