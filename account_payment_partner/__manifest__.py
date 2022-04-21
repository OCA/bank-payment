# Copyright 2014 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2014 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Payment Partner",
    "version": "14.0.1.5.0",
    "category": "Banking addons",
    "license": "AGPL-3",
    "summary": "Adds payment mode on partners and invoices",
    "author": "Akretion, Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/bank-payment",
    "development_status": "Mature",
    "depends": ["account_payment_mode"],
    "data": [
        "views/res_partner_view.xml",
        "views/account_move_view.xml",
        "views/account_move_line.xml",
        "views/account_payment_mode.xml",
        "views/report_invoice.xml",
        "reports/account_invoice_report_view.xml",
    ],
    "demo": ["demo/partner_demo.xml"],
    "installable": True,
}
