# -*- coding: utf-8 -*-
# Copyright 2013-2016 Akretion - Alexis de Lattre
# Copyright 2014-2017 Tecnativa - Pedro M. Baeza
# Copyright 2016 Tecnativa - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Banking PAIN Base Module',
    'summary': 'Base module for PAIN file generation',
    'version': '10.0.1.1.1',
    'license': 'AGPL-3',
    'author': "Akretion, "
              "Noviat, "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/bank-payment',
    'category': 'Hidden',
    'depends': ['account_payment_order'],
    'external_dependencies': {
        'python': ['unidecode', 'lxml'],
    },
    'data': [
        'security/security.xml',
        'views/account_payment_line.xml',
        'views/account_payment_order.xml',
        'views/bank_payment_line_view.xml',
        'views/account_payment_mode.xml',
        'views/account_config_settings.xml',
        'views/account_payment_method.xml',
    ],
    'post_init_hook': 'set_default_initiating_party',
    'installable': True,
}
