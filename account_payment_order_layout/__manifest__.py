# Copyright 2023 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Payment Order Layout",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "Jarsa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/bank-payment",
    "development_status": "Beta",
    "category": "Banking addons",
    "depends": ["account_payment_order"],
    "data": [
        "views/account_payment_mode_layout_views.xml",
        "views/account_payment_mode_layout_line_views.xml",
        "views/account_payment_mode_views.xml",
        "security/ir.model.access.csv",
        "security/ir_rule_data.xml",
    ],
    "demo": [],
    "installable": True,
}
