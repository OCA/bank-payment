# Copyright 2023 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Payment Order currency",
    "version": "14.0.0.1.0",
    "license": "AGPL-3",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/bank-payment",
    "category": "Banking addons",
    "depends": ["account_payment_order"],
    "data": [
        "wizard/account_payment_line_create_view.xml",
        "views/account_payment_mode.xml",
    ],
    "installable": True,
}
