# -*- coding: utf-8 -*-
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Account Payment Expense',
    'version': '9.0.1.0.0',
    'license': 'AGPL-3',
    'author': "brain-tec AG, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/bank-payment',
    'category': 'Banking addons',
    'depends': ['account_payment_order',
                'hr_expense',
                ],
    'installable': True,
    'auto_install': True,
}
