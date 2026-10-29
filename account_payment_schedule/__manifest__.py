# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Payment Schedule",
    "summary": "Schedule open items by payment date and turn each date "
    "into a draft payment order",
    "version": "16.0.1.0.0",
    "development_status": "Beta",
    "category": "Banking addons",
    "license": "AGPL-3",
    "author": "KMEE,Odoo Community Association (OCA)",
    "maintainers": ["mileo"],
    "website": "https://github.com/OCA/bank-payment",
    "depends": ["account_payment_order"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/account_payment_schedule_order.xml",
        "views/account_move_line.xml",
        "views/account_payment_order.xml",
        "views/res_config_settings.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "account_payment_schedule/static/src/views/*",
        ],
    },
    "pre_init_hook": "pre_init_hook",
    "installable": True,
}
