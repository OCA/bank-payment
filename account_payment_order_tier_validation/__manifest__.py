# Copyright 2021 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Payment Order Tier Validation",
    "summary": """Extends the functionality of Payment Orders
        to support a tier validation process.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "maintainers": ["marcelsavegnago"],
    "website": "https://github.com/OCA/bank-payment",
    "depends": ["account_payment_order", "base_tier_validation"],
    "data": [
        "views/account_payment_order.xml",
    ],
}
