# -*- coding: utf-8 -*-
# © 2010-2015 Akretion (www.akretion.com)
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 Antiun Ingenieria S.L. - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Banking SEPA Credit Transfer',
    'summary': 'Create SEPA XML files for Credit Transfers',
    'version': '8.0.0.5.1',
    'license': 'AGPL-3',
    'author': "Akretion, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Antiun Ingeniería S.L., "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/bank-payment',
    'category': 'Banking addons',
    'depends': ['account_banking_pain_base'],
    'data': [
        'wizard/export_sepa_view.xml',
        'data/payment_type_sepa_sct.xml',
    ],
    'demo': [
        'demo/sepa_credit_transfer_demo.xml'
    ],
    'installable': True,
}
