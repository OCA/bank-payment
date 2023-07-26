# Copyright 2017 Tecnativa - Luis M. Ontalba
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Account Payment Order Return',
    'version': '12.0.1.0.0',
    'category': 'Banking addons',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/bank-payment',
    'depends': [
        'account_payment_return',
        'account_payment_order',
    ],
    'data': [
        'wizards/account_payment_line_create_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': True,
}
