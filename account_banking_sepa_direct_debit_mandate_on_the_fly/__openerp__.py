# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": "Create mandates for payment orders",
    "version": "1.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "complexity": "normal",
    "description": """
Introduction
------------

When switching to SEPA payments, the mandates to be created can be a
serious show stopper. Usually, they are available in one form or the other,
but not in OpenERP. This plugin adds a button on payment orders to create
mandates for the current payment order where necessary.

Configuration
-------------

By default, this module creates one-off mandates. If you rather want to create
recurring mandates (i.e. because your available mandates are recurring ones),
set the config parameter
'account.banking.sepa.direct.debit.create.mandates' to 'recurrent'.

Attention
---------

Only use this if you actually have the mandates!
    """,
    "category": "Banking addons",
    "depends": [
        'account_banking_sepa_direct_debit',
    ],
    "data": [
        "view/payment_order.xml",
    ],
    "js": [
    ],
    "css": [
    ],
    "qweb": [
    ],
    "test": [
    ],
    "auto_install": False,
    "installable": True,
    "application": False,
    "external_dependencies": {
        'python': [],
    },
}
