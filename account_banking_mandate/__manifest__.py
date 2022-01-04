# -*- coding: utf-8 -*-
# © 2014 Compassion CH - Cyril Sester <csester@compassion.ch>
# © 2014 Tecnativa - Pedro M. Baeza
# © 2015-2016 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Banking Mandate',
    'summary': 'Banking mandates',
    'version': '10.0.1.1.0',
    'license': 'AGPL-3',
    'author': "Compassion CH, "
              "Tecnativa, "
              "Akretion, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/bank-payment',
    'category': 'Banking addons',
    'depends': [
        'account_payment_order',
    ],
    'data': [
        'views/account_banking_mandate_view.xml',
        'views/account_payment_method.xml',
        'views/account_invoice_view.xml',
        'views/account_payment_line.xml',
        'views/res_partner_bank_view.xml',
        'views/res_partner.xml',
        'views/bank_payment_line_view.xml',
        'views/account_move_line.xml',
        'data/mandate_reference_sequence.xml',
        'security/mandate_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
