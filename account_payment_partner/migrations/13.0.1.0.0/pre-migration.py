# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade  # pylint: disable=W7936


@openupgrade.migrate()
def migrate(env, version):
    # Pre-create column for avoiding to trigger the compute
    openupgrade.logged_query(
        env.cr, "ALTER TABLE account_move ADD payment_mode_id int4"
    )
