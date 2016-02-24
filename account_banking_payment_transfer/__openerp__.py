# -*- coding: utf-8 -*-
# © 2009 EduSense BV (<http://www.edusense.nl>)
# © 2011-2013 Therp BV (<http://therp.nl>)
# © 2013-2014 ACSONE SA (<http://acsone.eu>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Banking - Payments Transfer Account',
    'version': '8.0.0.3.0',
    'license': 'AGPL-3',
    'author': "Banking addons community,Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/banking',
    'category': 'Banking addons',
    'post_init_hook': 'set_date_sent',
    'depends': [
        'account_banking_payment_export',
    ],
    'data': [
        'view/payment_mode.xml',
        'workflow/account_payment.xml',
        'view/account_payment.xml',
    ],
    'test': [
        'test/data.yml',
        'test/test_payment_method.yml',
        'test/test_partial_payment_refunded.yml',
        'test/test_partial_payment_transfer.yml',


    ],
    'auto_install': False,
    'installable': True,
}
