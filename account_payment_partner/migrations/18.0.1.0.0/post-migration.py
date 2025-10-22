# Copyright 2025 Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade, openupgrade_180


@openupgrade.migrate()
def migrate(env, version):
    openupgrade_180.convert_company_dependent(
        env, "res.partner", "supplier_payment_mode_id"
    )
    openupgrade_180.convert_company_dependent(
        env, "res.partner", "customer_payment_mode_id"
    )
    # Drop temporary ir_property table created in pre-migration
    cr = env.cr
    cr.execute(
        """
        SELECT EXISTS (
            SELECT FROM pg_tables
            WHERE schemaname = 'public' AND tablename = 'ir_property'
        ) AND EXISTS (
            SELECT FROM pg_tables
            WHERE schemaname = 'public' AND tablename = '_ir_property'
        )
        """
    )
    if cr.fetchone()[0]:
        openupgrade.logged_query(cr, "DROP TABLE IF EXISTS ir_property")
