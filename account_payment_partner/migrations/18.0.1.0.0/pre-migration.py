# Copyright 2025 Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def migrate(cr, version):
    """Create temporary copy of _ir_property as ir_property.

    In Odoo 18.0, the ir_property table was renamed to _ir_property.
    However, openupgrade_180.convert_company_dependent() still references
    the old table name. This pre-migration creates a temporary copy to
    allow the post-migration to work correctly.
    """
    # Check if _ir_property exists and ir_property doesn't
    cr.execute(
        """
        SELECT EXISTS (
            SELECT FROM pg_tables
            WHERE schemaname = 'public' AND tablename = '_ir_property'
        )
        """
    )
    if cr.fetchone()[0]:
        cr.execute(
            """
            SELECT EXISTS (
                SELECT FROM pg_tables
                WHERE schemaname = 'public' AND tablename = 'ir_property'
            )
            """
        )
        if not cr.fetchone()[0]:
            # Create temporary copy of _ir_property as ir_property
            openupgrade.logged_query(
                cr,
                """
                CREATE TABLE ir_property AS
                SELECT * FROM _ir_property
                """,
            )
