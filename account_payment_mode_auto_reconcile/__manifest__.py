# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Account Payment Mode Auto Reconcile",
    "summary": "Reconcile outstanding credits according to payment mode",
    "version": "10.0.1.0.0",
    "category": "Banking addons",
    "website": "https://github.com/OCA/bank-payment",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "account_payment_partner",
    ],
    "data": [
        "views/account_invoice.xml",
        "views/account_payment_mode.xml",
    ],
    "demo": [
        "demo/account_payment_mode.xml",
    ],
}
