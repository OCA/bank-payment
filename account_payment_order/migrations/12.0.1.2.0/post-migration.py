# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env, 'account_payment_order', [
            'bank_payment_line_seq',
            'account_payment_line_seq',
            'account_payment_order_seq',
        ], True,
    )
