# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Payment Order Email",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "maintainers": ["ursais"],
    "website": "https://github.com/OCA/bank-payment",
    "category": "Accounting",
    "depends": ["account_payment_order", "account_payment_mode"],
    "data": [
        "data/mail_template.xml",
        "views/account_payment_mode_view.xml",
        "views/account_payment_order_view.xml",
    ],
    "installable": True,
}
