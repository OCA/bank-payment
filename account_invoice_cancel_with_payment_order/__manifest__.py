# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Invoice Cancel With Payment Order',
    'summary': """
        Allow to cancel an invoice (and its moves)
        when linked with payments""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': ['rousseldenis'],
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/bank-payment',
    'depends': [
        'account',
        'account_payment_order',
    ],
    'data': [
        'wizards/validate_invoice_cancel.xml',
    ],
}
