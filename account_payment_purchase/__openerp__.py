# -*- coding: utf-8 -*-
# © 2014-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# TODO : With the new workflow for supplier invoices where the user
# creates the supplier invoice then pulls the purchase orders,
# I think we should drop this module in v9... shoulnd't we ?
{
    'name': 'Account Payment Purchase',
    'version': '8.0.1.0.0',
    'category': 'Banking addons',
    'license': 'AGPL-3',
    'summary': "Adds Bank Account and Payment Mode on Purchase Orders",
    'author': "Akretion, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/bank-payment',
    'depends': [
        'purchase',
        'account_payment_partner'
    ],
    'conflicts': ['purchase_payment'],
    'data': [
        'views/purchase_order_view.xml',
    ],
    'installable': False,
    'auto_install': True,
}
