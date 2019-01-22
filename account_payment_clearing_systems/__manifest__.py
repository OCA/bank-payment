# -*- coding: utf-8 -*-
# Copyright 2018 brain-tec AG (https://www.braintec-group.com/)
# @author: Timka Piric Muratovic, Tobias Bächle
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Account Payment Clearing Systems',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Odoo Community Association (OCA), brain-tec AG',
    'website': 'https://github.com/OCA/bank-payment',
    'category': 'Banking addons',
    'depends': [
        'account_banking_pain_base',
    ],
    'data': [
        'views/res_bank_view.xml',
    ],
    'installable': True,
}
