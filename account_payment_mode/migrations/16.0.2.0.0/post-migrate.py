# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Migrate note field from Text to Html"""

    if openupgrade.column_exists(env.cr, "account_payment_mode", "note"):
        records = env["account.payment.mode"].search_count([("note", "!=", False)])
        if records:
            openupgrade.convert_field_to_html(
                env.cr, "account_payment_mode", "note", "note", False, True
            )
