# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Payment Schedule API",
    "summary": "Payment schedule with the status given by the bank API: "
    "refused items come back to the schedule",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "category": "Banking addons",
    "license": "AGPL-3",
    "author": "KMEE,Odoo Community Association (OCA)",
    "maintainers": ["mileo"],
    "website": "https://github.com/OCA/bank-payment",
    "depends": ["account_payment_schedule", "account_payment_order_api"],
    "data": ["views/account_move_line.xml"],
    "auto_install": True,
    "installable": True,
}
