# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Payment Method Or Mode Fs Storage",
    "summary": """
        Add the possibility to specify on the payment method or on the
        payment mode depending on the company,
        a storage where files generated will be pushed to upon payment
    """,
    "version": "16.0.1.0.5",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/bank-payment",
    "depends": [
        "account_banking_sepa_credit_transfer",
        "fs_storage",
        "account_payment_mode",
    ],
    "data": [
        "security/res_groups.xml",
        "security/fs_storage.xml",
        "views/res_config_settings.xml",
        "views/account_payment_mode.xml",
        "views/account_payment_method.xml",
    ],
    "demo": [],
}
