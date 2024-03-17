# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Payment Order Tier Validation",
    "summary": "Extends the functionality of Account Payment Orders to "
    "support a tier validation process.",
    "version": "15.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/bank-payment",
    "author": "Jarsa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["account_payment_order", "base_tier_validation"],
    "data": [
        "views/account_payment_order_view.xml",
    ],
}
