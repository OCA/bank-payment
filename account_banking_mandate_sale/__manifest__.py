# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Banking Mandate Sale',
    'version': '12.0.1.0.1',
    'category': 'Banking addons',
    'license': 'AGPL-3',
    'summary': "Adds mandates on sale orders",
    'author': "Odoo Community Association (OCA), "
              "Akretion",
    'website': 'https://github.com/OCA/bank-payment',
    'depends': [
        'account_payment_sale',
        'account_banking_mandate',
    ],
    'data': [
        'views/sale_order.xml',
    ],
    'installable': True,
}
