# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Migrate note field from Text to Html"""
    openupgrade.logged_query(
        env.cr, "UPDATE account_payment_mode SET note = '{}'::jsonb where note is NULL"
    )
    openupgrade.convert_field_to_html(
        env.cr, "account_payment_mode", "note", "note", False, True
    )
