# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Account Payment Mode Default Account",
    "summary": "Set Receivable or Payable account according to payment mode",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Accounting/Accounting",
    "website": "https://github.com/OCA/bank-payment",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "account_payment_partner",
    ],
    "data": [
        "views/account_payment_mode.xml",
    ],
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
}
