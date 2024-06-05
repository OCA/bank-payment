# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Vendor Bank Account Default",
    "summary": "Set a default bank account on partners for their vendor bills",
    "version": "17.0.1.0.0",
    "development_status": "Beta",
    "category": "Banking addons",
    "website": "https://github.com/OCA/bank-payment",
    "author": "Sygel, Odoo Community Association (OCA)",
    "maintainers": ["tisho99"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
        "account_payment_partner",
    ],
    "data": [
        "views/res_partner_views.xml",
    ],
}
