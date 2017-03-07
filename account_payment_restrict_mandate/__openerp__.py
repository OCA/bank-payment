# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Restrict debits on mandates",
    "version": "8.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "summary": "Set maximum amount per period on a mandate",
    "depends": [
        'account_banking_mandate',
        'field_rrule',
    ],
    "data": [
        "views/payment_order.xml",
        "views/account_banking_mandate.xml",
    ],
}
