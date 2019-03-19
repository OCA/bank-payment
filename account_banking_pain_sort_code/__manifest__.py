# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Banking Pain Sort Code',
    'summary': """
        Adds the bank Sort Code in payment order""",
    'version': '10.0.1.0.1',
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': ['rousseldenis'],
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/bank-payment',
    'depends': [
        'partner_bank_sort_code',
        'account_banking_pain_base',
    ],
}
