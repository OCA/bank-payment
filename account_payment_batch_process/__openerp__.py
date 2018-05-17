# -*- coding: utf-8 -*-
# Copyright 2017 Ursa Information Systems <http://www.ursainfosystems.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Batch Payments Processing",
    "summary": "Process Payments in Batch",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "Ursa Information Systems, Odoo Community Association (OCA)",
    "category": "Generic Modules/Payment",
    "website": "http://www.ursainfosystems.com",
    "depends": [
        "account",
        "account_check_printing",
    ],
    "data": [
        "wizard/invoice_batch_process_view.xml",
        "views/invoice_view.xml"
    ],
    "installable": True,
}
