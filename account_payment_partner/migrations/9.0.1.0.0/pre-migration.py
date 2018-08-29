# -*- coding: utf-8 -*-
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version=None):
    openupgrade.rename_property(
        env.cr, 'res.partner', 'supplier_payment_mode',
        'supplier_payment_mode_id',
    )
    openupgrade.rename_property(
        env.cr, 'res.partner', 'customer_payment_mode',
        'customer_payment_mode_id',
    )
    openupgrade.rename_fields(
        env, [
            ('res.partner', 'res_partner', 'supplier_payment_mode',
             'supplier_payment_mode_id'),
            ('res.partner', 'res_partner', 'customer_payment_mode',
             'customer_payment_mode_id'),
        ],
    )
