# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "IPpay Payment",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "summary": "IPpay Payment",
    "author": "Open Source Integrators",
    "maintainer": "Open Source Integrators",
    "website": "http://www.opensourceintegrators.com",
    "category": "Accounting",
    "depends": ['payment_authorize'],
    "data": [
        "data/ippay_payment_data.xml",
        "data/account_payment_method.xml",
        "wizards/add_cc_token_wizard_view.xml",
        "views/payment_view.xml",
        "views/partner_view.xml",
        "views/account_invoice_view.xml",
    ],
    "installable": True,
    'external_dependencies': {'python': ['xmltodict']}
}
