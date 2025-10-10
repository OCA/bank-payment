# Copyright 2016-2020 Akretion France (<https://www.akretion.com>)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Payment Mode",
    "version": "19.0.1.0.0",
    "development_status": "Mature",
    "license": "AGPL-3",
    "summary": "Adds payment mode on partners and invoices",
    "author": "Akretion, Tecnativa,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/bank-payment",
    "category": "Banking addons",
    "depends": ["account"],
    "data": [
        "security/account_payment_partner_security.xml",
        "security/account_payment_mode.xml",
        "security/ir.model.access.csv",
        "views/res_partner_view.xml",
        "views/account_move_view.xml",
        "views/account_move_line.xml",
        "views/account_payment_method.xml",
        "views/account_payment_mode.xml",
        "views/account_journal.xml",
        "views/report_invoice.xml",
        "reports/account_invoice_report_view.xml",
    ],
    "demo": ["demo/payment_demo.xml", "demo/partner_demo.xml"],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}
