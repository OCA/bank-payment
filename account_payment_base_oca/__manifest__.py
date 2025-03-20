# Copyright 2024-2025 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Payment Base OCA",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": "OCA extensions to native payment objects of Odoo",
    "author": "Akretion,Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "development_status": "Mature",
    "website": "https://github.com/OCA/bank-payment",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_payment_method.xml",
        "views/account_payment_method_line.xml",
        "views/account_move.xml",
        "reports/account_invoice_report_view.xml",
        "security/ir_rule.xml",
    ],
    "demo": ["demo/demo.xml"],
    "installable": True,
}
