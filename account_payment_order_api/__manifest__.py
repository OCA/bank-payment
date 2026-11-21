# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Payment Order API",
    "summary": "Send payment orders to the bank through an API, "
    "with status and accounting per line",
    "version": "16.0.1.0.0",
    "development_status": "Beta",
    "category": "Banking addons",
    "license": "AGPL-3",
    "author": "KMEE,Odoo Community Association (OCA)",
    "maintainers": ["mileo"],
    "website": "https://github.com/OCA/bank-payment",
    "depends": ["account_payment_order", "auth_totp"],
    "data": [
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "data/ir_cron.xml",
        "views/account_payment_mode.xml",
        "views/account_payment_api_batch.xml",
        "views/account_payment_order.xml",
        "views/res_config_settings.xml",
        "wizard/account_payment_api_second_factor.xml",
    ],
    "installable": True,
}
