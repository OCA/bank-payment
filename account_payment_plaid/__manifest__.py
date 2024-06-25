# Copyright 2024 Binhex - Adasat Torres de León.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Payment Plaid",
    "version": "14.0.1.0.0",
    "category": "Connector",
    "website": "https://github.com/OCA/bank-payment",
    "author": "Binhex, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["base", "account", "purchase"],
    "data": [
        "security/ir.model.access.csv",
        "views/assets.xml",
        "views/account_move_views.xml",
        "views/res_partner_views.xml",
        "views/res_config_settings_views.xml",
        "views/plaid_account_views.xml",
        "views/plaid_transfer_views.xml",
        "wizard/account_payment_plaid_wizard_views.xml",
        "wizard/plaid_transfer_sandbox_simulation_wizard_views.xml",
        "data/sync_transfer_events_cron.xml",
        "data/payment_method_data.xml",
    ],
    "external_dependencies": {
        "python": ["plaid-python"],
    },
}
