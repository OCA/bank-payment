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
    "depends": ['osi_add_credit_card'],
    "data": [
        "data/ippay_payment_data.xml",
        "views/payment_view.xml",
    ],
    "installable": True,
    'external_dependencies': {'python': ['xmltodict']}
}
