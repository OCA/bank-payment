# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Credit Card",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "summary": "Use stored Credit Cards to pay Invoices from the Accounting App",
    "author": "Open Source Integrators",
    "maintainer": "Open Source Integrators",
    "website": "http://www.opensourceintegrators.com",
    "category": "Accounting",
    "depends": ['payment'],
    "data": [
        "security/payment_security.xml",
        "wizards/add_cc_token_wizard_view.xml",
        "views/res_partner_view.xml",
        "views/account_invoice_view.xml",
        "views/payment_token_view.xml",
    ],
    "installable": True,
}
