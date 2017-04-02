# -*- coding: utf-8 -*-
# © 2013-2016 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# © 2014 Tecnativa - Pedro M. Baeza
# © 2016 Tecnativa - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Banking PAIN Base Module',
    'summary': 'Base module for PAIN file generation',
    'version': '9.0.1.0.0',
    'license': 'AGPL-3',
    'author': "Akretion, "
              "Noviat, "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/bank-payment',
    'contributors': ['Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>'],
    'category': 'Hidden',
    'depends': ['account_payment_order'],
    'external_dependencies': {
        'python': ['unidecode', 'lxml'],
    },
    'data': [
        'views/account_payment_line.xml',
        'views/account_payment_order.xml',
        'views/bank_payment_line_view.xml',
        'views/account_payment_mode.xml',
        'views/res_company_view.xml',
        'views/account_payment_method.xml',
    ],
    'post_init_hook': 'set_default_initiating_party',
    'installable': True,
}
