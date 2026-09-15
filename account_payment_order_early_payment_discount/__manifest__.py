# Copyright 2026 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Payment Orders with Early Payment Discount",
    "summary": "Take the early payment discount in payment orders and pay "
    "preferred suppliers on their early payment date",
    "version": "19.0.1.0.0",
    "category": "Banking addons",
    "website": "https://github.com/OCA/bank-payment",
    "author": "Jarsa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "development_status": "Beta",
    "depends": ["account_payment_order", "account_supplier_early_payment_discount"],
    "data": [
        "security/account_payment_line_security.xml",
        "views/account_payment_line_views.xml",
        "views/res_partner_views.xml",
    ],
    "installable": True,
}
