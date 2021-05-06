# Copyright 2012-2021 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account payment prevent post",
    "summary": "Prevent Odoo to autovalidate entries",
    "version": "14.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "category": "Banking addons",
    "website": "https://github.com/OCA/bank-payment",
    "license": "AGPL-3",
    "depends": [
        "account",
    ],
    "data": [
        "views/res_config_settings.xml",
    ],
    "auto_install": False,
    "installable": True,
}
