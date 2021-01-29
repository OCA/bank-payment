# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Payment Order Void Lines",
    "summary": "Cancel payment order lines",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators, " "Odoo Community Association (OCA)",
    "category": "Banking Addons",
    "maintainers": [],
    "website": "https://github.com/OCA/bank-payment",
    "depends": [
        "account_payment_order",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/bank_payment_line.xml",
        "views/account_payment_line.xml",
        "wizards/cancel_payment_line.xml",
    ],
    "installable": True,
}
