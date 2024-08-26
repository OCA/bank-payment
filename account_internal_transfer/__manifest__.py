# Copyright 2024 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Internal Transfer",
    "summary": """
        Account Internal Transfer""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/bank-payment",
    "depends": ["account", "account_menu", "account_payment_order"],
    "data": [
        "views/account_internal_transfer_views.xml",
        "views/res_config_settings.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [],
}
