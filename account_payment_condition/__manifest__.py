# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Payment Condition',
    'summary': """
        Relate payment mode with payment term""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE,Odoo Community Association (OCA)',
    'website': 'https://github.com/oca/bank-payment',
    'development_status': 'Alpha',
    'depends': [
        'account_payment_partner',
        'account',
    ],
    'maintainers': ['mileo'],
    'data': [
        'security/account_payment_condition.xml',
        'views/account_payment_condition_view.xml',
        'views/account_invoice_view.xml',
    ],
    'demo': [
        'demo/account_payment_condition.xml',
    ],
}
