# -*- coding: utf-8 -*-
# © 2014 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Payment Partner',
    'version': '8.0.0.2.0',
    'category': 'Banking addons',
    'license': 'AGPL-3',
    'summary': 'Adds payment mode on partners and invoices',
    'author': "Akretion, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/bank-payment',
    'depends': ['account_banking_payment_export'],
    'data': [
        'views/res_partner_view.xml',
        'views/account_invoice_view.xml',
        'views/report_invoice.xml',
        'views/payment_mode.xml',
        'security/ir.model.access.csv',
        'wizard/payment_order_create_view.xml',
    ],
    'demo': ['demo/partner_demo.xml'],
    'installable': True,
}
