# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "Account Cash Discount Stock",

    'summary': """Link between account cash discount and stock module""",
    'author': 'ACSONE SA/NV,'
              'Odoo Community Association (OCA)',
    'website': "http://acsone.eu",
    'category': 'Accounting',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'account_cash_discount_payment_term',
        'stock',
    ],
    'data': [],
    'auto_install': True,
}
