# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Banking Mandate Sale Contact",
    "summary": "Add a specific contact mandate to sale orders",
    "version": "16.0.1.0.1",
    "development_status": "Beta",
    "category": "Banking addons",
    "website": "https://github.com/OCA/bank-payment",
    "author": "Alberto Martínez, Odoo Community Association (OCA)",
    "maintainers": ["tisho99"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["account_banking_mandate_contact", "account_banking_mandate_sale"],
    "data": ["views/res_config_settings.xml", "views/res_partner.xml"],
}
