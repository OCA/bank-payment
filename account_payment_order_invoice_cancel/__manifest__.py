# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Payment Order Invoice Cancel',
    'summary': """
        Allow to reset to draft an invoice which is linked to a payment order.
    """,
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/bank-payment',
    'depends': [
        'account_payment_order',
    ],
    'data': [
        'wizards/account_payment_order_invoice_cancel.xml',
    ],
}
