# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Payment Method Fs Storage",
    "summary": """
        Add the possibility to specify on the payment method,
        a storage where files generated will be pushed to upon payment
    """,
    "version": "16.0.1.0.2",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/bank-payment",
    "depends": [
        "account_banking_sepa_credit_transfer",
        "fs_storage",
    ],
    "data": [
        "views/fs_storage.xml",
        "views/account_payment_method.xml",
    ],
    "demo": [],
}
