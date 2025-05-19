from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env.cr.execute(
        """
        SELECT
            id
        FROM account_payment_mode
        WHERE note::text ~* '<[^>]+>' LIMIT 1
        """
    )
    if env.cr.rowcount == 0:
        # If there are no HTML tags in the note field, we can convert it to HTML
        openupgrade.convert_field_to_html(
            env.cr, "account_payment_mode", "note", "note", False, True
        )
