# Copyright 2013-2020 Akretion (www.akretion.com)
# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2014-2022 Tecnativa - Pedro M. Baeza
# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Banking SEPA Direct Debit",
    "summary": "Create SEPA files for Direct Debit",
    "version": "16.0.1.4.5",
    "license": "AGPL-3",
    "author": "Akretion, Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/bank-payment",
    "category": "Banking addons",
    "depends": ["account_banking_pain_base", "account_banking_mandate"],
    "assets": {
        "web.report_assets_common": [
            "/account_banking_sepa_direct_debit/static/src/css/report.css"
        ],
    },
    "data": [
        "views/account_banking_mandate_view.xml",
        "views/res_config_settings.xml",
        "views/account_payment_mode.xml",
        "data/mandate_expire_cron.xml",
        "data/account_payment_method.xml",
        "data/report_paperformat.xml",
        "reports/sepa_direct_debit_mandate.xml",
        "views/report_sepa_direct_debit_mandate.xml",
        "data/mail_template_data.xml",
    ],
    "demo": ["demo/sepa_direct_debit_demo.xml"],
    "installable": True,
}
