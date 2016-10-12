# -*- coding: utf-8 -*-
# © 2014 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Payment Partner',
    'version': '10.0.1.0.0',
    'category': 'Banking addons',
    'license': 'AGPL-3',
    'summary': 'Adds payment mode on partners and invoices',
    'author': "Akretion, "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/bank-payment',
    'depends': ['account_payment_mode'],
    'data': [
        'views/res_partner_view.xml',
        'views/account_invoice_view.xml',
        'views/account_move_line.xml',
        'views/report_invoice.xml',
    ],
    'demo': ['demo/partner_demo.xml'],
    'installable': True,
}
