# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Payement Order Transfer Journal",
    "summary": """
        Add the possibility to book payement order operations on a transfert journal.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/bank-payment",
    "depends": ["account_payment_order"],
    "data": [
        "views/account_journal.xml",
    ],
    "demo": [],
}
