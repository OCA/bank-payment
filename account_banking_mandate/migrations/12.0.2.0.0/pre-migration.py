# -*- coding: utf-8 -*-
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

column_renames = {
    'account_banking_mandate': [
        ('scan', None),
    ],
}


@openupgrade.migrate()
def migrate(cr, version):
    if openupgrade.column_exists(cr, 'account_banking_mandate', 'scan'):
        openupgrade.rename_columns(cr, column_renames)
