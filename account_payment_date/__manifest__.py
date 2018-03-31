# -*- coding: utf-8 -*-
# © <2018> <Cristian Salamea>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Accounting Payments Dates',
    'version': '10.0.1.0.0',
    'category': 'Accounting',
    'author': "PriseHub, Odoo Community Association (OCA)",
    'website': 'http://www.prisehub.com',
    'license': 'AGPL-3',
    'depends': [
        'account_payment_order'
    ],
    'data': [
        'views/payment_views.xml',
    ],
    'installable': True,
}
