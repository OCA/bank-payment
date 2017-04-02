# -*- coding: utf-8 -*-
# © 2009 EduSense BV (<http://www.edusense.nl>)
# © 2011-2013 Therp BV (<http://therp.nl>)
# © 2013-2014 ACSONE SA (<http://acsone.eu>).
# © 2014-2016 Tecnativa - Pedro M. Baeza
# © 2016 Akretion (<http://www.akretion.com>).
# © 2016 Aselcis Consulting (<http://www.aselcis.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Payment Order',
    'version': '9.0.1.1.2',
    'license': 'AGPL-3',
    'author': "ACSONE SA/NV, "
              "Therp BV, "
              "Tecnativa, "
              "Akretion, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/bank-payment',
    'category': 'Banking addons',
    'depends': [
        'account_payment_partner',
        'base_iban',  # for manual_bank_tranfer
        'document',  # to see the attachments on payment.order
    ],
    'data': [
        'security/payment_security.xml',
        'security/ir.model.access.csv',
        'wizard/account_payment_line_create_view.xml',
        'wizard/account_invoice_payment_line_multi_view.xml',
        'views/account_payment_mode.xml',
        'views/account_payment_order.xml',
        'views/account_payment_line.xml',
        'views/bank_payment_line.xml',
        'views/account_move_line.xml',
        'views/ir_attachment.xml',
        'views/account_invoice_view.xml',
        'data/payment_seq.xml',
    ],
    'demo': ['demo/payment_demo.xml'],
    'installable': True,
}
