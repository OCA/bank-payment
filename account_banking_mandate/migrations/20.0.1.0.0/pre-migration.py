# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    """ir.model.access and ir.rule were merged into ir.access in Odoo 20.
    Drop the stale external ids of this module that still point to the removed
    models, otherwise loading ir.access.csv fails with "found record of
    different model" (the ids are re-created by the new csv).
    """
    if not version:
        return
    for table, model in (
        ("ir_model_access", "ir.model.access"),
        ("ir_rule", "ir.rule"),
    ):
        cr.execute("SELECT to_regclass(%s)", (table,))
        if cr.fetchone()[0]:
            cr.execute(
                f"""
                DELETE FROM {table} WHERE id IN (
                    SELECT res_id FROM ir_model_data
                    WHERE module = 'account_banking_mandate' AND model = %s
                )
                """,
                (model,),
            )
    cr.execute(
        """
        DELETE FROM ir_model_data
        WHERE module = 'account_banking_mandate'
        AND model IN ('ir.model.access', 'ir.rule')
        """
    )
