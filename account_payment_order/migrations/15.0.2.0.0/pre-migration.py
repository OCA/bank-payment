# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.table_exists(env.cr, "bank_payment_line"):
        return  # if coming from 14.2.0.0
    openupgrade.remove_tables_fks(env.cr, ["bank_payment_line"])
