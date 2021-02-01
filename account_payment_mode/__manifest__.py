# © 2016 Akretion (<https://www.akretion.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Payment Mode",
    "version": "13.0.1.2.0",
    "development_status": "Production/Stable",
    "license": "AGPL-3",
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/bank-payment",
    "category": "Banking addons",
    "depends": ["account"],
    "data": [
        "security/account_payment_mode.xml",
        "security/ir.model.access.csv",
        "views/account_payment_method.xml",
        "views/account_payment_mode.xml",
        "views/res_partner_bank.xml",
        "views/res_partner.xml",
        "views/account_journal.xml",
    ],
    "demo": ["demo/payment_demo.xml"],
    "installable": True,
}
