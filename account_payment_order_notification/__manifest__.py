# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Payment Order Notification",
    "version": "16.0.1.0.0",
    "category": "Banking addons",
    "website": "https://github.com/OCA/bank-payment",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["account_payment_order"],
    "installable": True,
    "data": [
        "security/ir.model.access.csv",
        "data/mail_template_data.xml",
        "wizard/wizard_account_payment_order_notification_views.xml",
        "views/account_payment_order_view.xml",
        "views/account_payment_order_notification_view.xml",
    ],
    "maintainers": ["victoralmau"],
}
