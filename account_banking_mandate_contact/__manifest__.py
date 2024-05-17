# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Banking Mandate Contact",
    "summary": "Assign specific banking mandates in contact level",
    "version": "15.0.1.0.2",
    "development_status": "Production/Stable",
    "category": "Banking addons",
    "website": "https://github.com/OCA/bank-payment",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["account_banking_mandate", "sale"],
    "data": [
        "views/res_partner.xml",
    ],
}
