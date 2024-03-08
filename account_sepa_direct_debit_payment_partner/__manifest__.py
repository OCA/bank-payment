# Copyright 2024 Akretion - Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account SEPA Direct Debit Payment Partner",
    "version": "14.0.1.0.0",
    "category": "Banking addons",
    "license": "AGPL-3",
    "summary": "Glue module between sepa_direct_debit and payment_partner",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/bank-payment",
    "development_status": "Beta",
    "depends": ["account_payment_partner", "account_banking_sepa_direct_debit"],
    "auto_install": True,
    "installable": True,
}
