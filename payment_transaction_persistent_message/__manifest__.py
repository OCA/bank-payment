# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Payment Transaction Persistent Message",
    "summary": """
        As Odoo is erasing state_message field after each state change,
        keep it in another field.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "maintainers": ["rousseldenis"],
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/bank-payment",
    "depends": [
        "payment",
    ],
    "data": [
        "views/payment_transaction.xml",
    ],
    "external_dependencies": {"python": ["openupgradelib"]},
    "post_init_hook": "post_init_hook",
}
