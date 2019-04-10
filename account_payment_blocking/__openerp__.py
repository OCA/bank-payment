# -*- coding: utf-8 -*-
{
    'name': 'Account Payment Blocking',
    'version': '8.0.1.1.0',
    'category': 'Banking addons',
    'summary': """
        Prevent invoices under litigation to be proposed in payment orders.
    """,
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'http://acsone.eu',
    'depends': [
        'base',
        'account_banking_payment_export'
    ],
    'data': [
        'view/account_invoice_view.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
