# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Payment Order Early Discount",
    "summary": "Native early payment discount of Odoo in payment orders",
    "version": "18.0.1.0.0",
    "category": "Banking addons",
    "license": "AGPL-3",
    "author": "ffiedl, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/bank-payment",
    "maintainers": ["ffiedl"],
    "depends": ["account_payment_order", "resource"],
    "data": [
        "views/account_payment_mode_views.xml",
        "views/account_payment_line_views.xml",
        "wizard/account_payment_line_create_views.xml",
    ],
    "installable": True,
}
