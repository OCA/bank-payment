# (C) 2019 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Payment Order Check',
    'version': '11.0.1.3.0',
    'license': 'AGPL-3',
    'author': "Creu Blanca, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/bank-payment',
    'category': 'Banking addons',
    'depends': [
        'account_payment_order',
        'account_check_printing_report_base',
        'account_check_printing',
    ],
    'data': [
        'views/account_payment_order.xml',
        'views/account_payment_mode.xml',
    ],
    'demo': [],
    'installable': True,
}
