# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Payment Order Partner",
    "summary": "Adds partner to payment orders and groups payment orders by partner.",
    "version": "14.0.1.0.0",
    "category": "Accounting Management",
    "website": "https://github.com/OCA/bank-payment",
    "author": "Open Source Integrators," "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["account_payment_order"],
    "data": [
        "views/payment_order_view.xml",
        "wizards/account_invoice_payment_line_multi_view.xml",
    ],
    "installable": True,
}
