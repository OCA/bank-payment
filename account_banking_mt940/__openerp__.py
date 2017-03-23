# -*- coding: utf-8 -*-
# © 2014-2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "MT940",
    "version": "7.0.1.0.1",
    'license': 'AGPL-3',
    "author": "Therp BV,Odoo Community Association (OCA)",
    "complexity": "expert",
    "description": """
This addon provides a generic parser for MT940 files. Given that MT940 is a
non-open non-standard of pure evil in the way that every bank cooks up its own
interpretation of it, this addon alone won't help you much. It is rather
intended to be used by other addons to implement the dialect specific to a
certain bank.

See account_banking_nl_ing_mt940 for an example on how to use it.
    """,
    "category": "Dependency",
    "depends": [
        'account_banking',
    ],
    "auto_install": False,
    "installable": True,
    "application": False,
}
