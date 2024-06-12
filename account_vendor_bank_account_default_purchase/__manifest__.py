# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Vendor Bank Account Default Purchase",
    "summary": "Set a default bank account purchase orders",
    "version": "17.0.1.0.0",
    "category": "Banking addons",
    "website": "https://github.com/OCA/bank-payment",
    "author": "Sygel, Odoo Community Association (OCA)",
    "maintainers": ["tisho99"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account_payment_purchase",
        "account_vendor_bank_account_default",
    ],
}
