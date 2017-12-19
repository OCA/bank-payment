# -*- coding: utf-8 -*-
# Copyright 2017-2018 Compassion CH (http://www.compassion.ch)
# @author: Marco Monzione <marco.mon@windowslive.com>, Emanuel Cino
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Account payment line cancel',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/bank-payment',
    'category': 'Banking addons',
    'depends': [
        'account_payment_order',
        'account_cancel',
    ],
    'data': [
        'views/invoice_view.xml',
        'views/payment_line_view.xml',
    ],
    'installable': True,
}
