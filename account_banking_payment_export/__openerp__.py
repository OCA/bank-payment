# -*- coding: utf-8 -*-
# © 2009 EduSense BV (<http://www.edusense.nl>)
# © 2011-2013 Therp BV (<http://therp.nl>)
# © 2013-2014 ACSONE SA (<http://acsone.eu>).
# © 2014-2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Banking - Payments Export Infrastructure',
    'version': '8.0.0.3.0',
    'license': 'AGPL-3',
    'author': "ACSONE SA/NV, "
              "Therp BV, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/bank-payment',
    'category': 'Banking addons',
    'depends': [
        'account_payment',
        'base_iban',  # for manual_bank_tranfer
        'document',  # to see the attachments on payment.order
    ],
    'data': [
        'views/account_payment.xml',
        'views/payment_mode.xml',
        'views/payment_mode_type.xml',
        'views/bank_payment_line.xml',
        'wizard/bank_payment_manual.xml',
        'wizard/payment_order_create_view.xml',
        'data/payment_mode_type.xml',
        'data/bank_payment_line_seq.xml',
        'workflow/account_payment.xml',
        'security/ir.model.access.csv',
    ],
    'demo': ['demo/banking_demo.xml'],
    'installable': True,
}
