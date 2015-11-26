# -*- coding: utf-8 -*-
# © 2014-2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "MT940 import for Dutch ING",
    "version": "7.0.1.1.1",
    "author": "Therp BV,Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    "complexity": "normal",
    "description": """
This addon imports the structured MT940 format as offered by the Dutch ING
bank.
    """,
    'category': 'Account Banking',
    'depends': [
        'account_banking_mt940',
    ],
    'images': [],  # Satisfy travis
    'auto_install': False,
    'installable': True,
    'application': False,
}
