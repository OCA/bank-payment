# -*- coding: utf-8 -*-
# © 2013-2015 Akretion (www.akretion.com)
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 Antiun Ingenieria S.L. - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Banking SEPA Direct Debit',
    'summary': 'Create SEPA files for Direct Debit',
    'version': '8.0.0.5.1',
    'license': 'AGPL-3',
    'author': "Akretion, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Antiun Ingeniería S.L., "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/bank-payment',
    'category': 'Banking addons',
    'depends': [
        'account_direct_debit',
        'account_banking_pain_base',
        'account_banking_mandate',
    ],
    'data': [
        'views/account_banking_mandate_view.xml',
        'views/res_company_view.xml',
        'views/payment_mode_view.xml',
        'wizard/export_sdd_view.xml',
        'data/mandate_expire_cron.xml',
        'data/payment_type_sdd.xml',
        'data/report_paperformat.xml',
        'reports/sepa_direct_debit_mandate.xml',
        'views/report_sepa_direct_debit_mandate.xml',
    ],
    'demo': ['demo/sepa_direct_debit_demo.xml'],
    'installable': True,
}
