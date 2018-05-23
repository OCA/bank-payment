# -*- coding: utf-8 -*-
# © 2014 Compassion CH - Cyril Sester <csester@compassion.ch>
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2015 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Banking Mandate',
    'summary': 'Banking mandates',
    'version': '8.0.0.2.1',
    'license': 'AGPL-3',
    'author': "Compassion CH, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Akretion, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/bank-payment',
    'category': 'Banking addons',
    'depends': [
        'account_banking_payment_export',
    ],
    'data': [
        'views/account_banking_mandate_view.xml',
        'views/account_invoice_view.xml',
        'views/account_payment_view.xml',
        'views/res_partner_bank_view.xml',
        'views/bank_payment_line_view.xml',
        'data/mandate_reference_sequence.xml',
        'security/mandate_security.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': ['test/banking_mandate.yml'],
    'installable': True,
}
