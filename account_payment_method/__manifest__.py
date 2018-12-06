# Copyright 2018 Eska Yazılım ve Danışmanlık A.Ş (www.eskayazilim.com.tr)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Manage Payment Methods',
    'summary': 'Adds payment method menu, views and access rights',
    'version': '12.0.1.0.0',
    'category': 'Accounting',
    'author': 'Eska, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/bank_payment/',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_payment_method_views.xml',
    ],
    'installable': True,
}
