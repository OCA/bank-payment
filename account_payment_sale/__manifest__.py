# Copyright 2014-2016 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# @author Alexis de Lattre <alexis.delattre@akretion.com>

{
    "name": "Account Payment Sale",
    "version": "16.0.1.0.3",
    "category": "Banking addons",
    "license": "AGPL-3",
    "summary": "Adds payment mode on sale orders",
    "author": "Akretion, " "Tecnativa, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/bank-payment",
    "depends": ["sale", "account_payment_partner"],
    "data": ["views/sale_order_view.xml", "views/sale_report_templates.xml"],
    "auto_install": True,
}
