# -*- coding: utf-8 -*-
# Copyright 2018 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    """Update database from previous versions, after updating module."""
    cr.execute(
        "UPDATE account_payment_mode "
        "SET show_bank_account_from_journal = true "
        "WHERE bank_account_link = 'fixed'"
    )
