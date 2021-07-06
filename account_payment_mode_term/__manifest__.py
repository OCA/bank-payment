# Copyright 2009 EduSense BV (<http://www.edusense.nl>)
# Copyright 2011 - 2013 Therp BV (<http://therp.nl>)
# Copyright 2014 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Banking - Payments Term Filter",
    "version": "13.0.1.0.0",
    "category": "Banking addons",
    "license": "AGPL-3",
    "author": "Banking addons community,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/bank-payment",
    "depends": ["account_payment_partner"],
    "data": [
        "views/account_move_view.xml",
        "views/account_payment_mode_view.xml",
        "views/account_payment_term_view.xml",
    ],
    "installable": True,
}
