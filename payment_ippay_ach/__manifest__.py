# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "IPPay ACH eCheck Payment Acquirer",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "summary": "IPPay ACH eCheck Payment",
    "author": "Open Source Integrators",
    "maintainer": "Open Source Integrators",
    "website": "http://www.opensourceintegrators.com",
    "category": "Accounting",
    "depends": ['payment'],
    "data": [
        "security/payment_security.xml",
        "data/payment_icon_data.xml",
        "data/ippay_payment_data.xml",
        "views/payment_view.xml",
    ],
    "development_status": "beta",
    "installable": True,
    'external_dependencies': {'python': ['xmltodict']}
}
