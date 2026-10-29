# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Payment Schedule Priority",
    "summary": "Payment priority on the schedule and a replan of the dates "
    "short of cash",
    "version": "16.0.1.0.0",
    "development_status": "Beta",
    "category": "Banking addons",
    "license": "AGPL-3",
    "author": "KMEE,Odoo Community Association (OCA)",
    "maintainers": ["mileo"],
    "website": "https://github.com/OCA/bank-payment",
    "depends": ["account_payment_schedule"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/account_payment_schedule_replan.xml",
        "views/account_move_line.xml",
        "views/res_partner.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "account_payment_schedule_priority/static/src/views/*",
        ],
    },
    "pre_init_hook": "pre_init_hook",
    "installable": True,
}
