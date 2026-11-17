# Copyright 2026 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def migrate(cr, version) -> None:
    if not version:
        return

    old_security_records = (
        ("ir.model.access", "ir_model_access", "access_account_banking_mandate"),
        (
            "ir.model.access",
            "ir_model_access",
            "access_account_banking_mandate_read",
        ),
        ("ir.rule", "ir_rule", "account_banking_mandate_rule"),
    )
    for model, table, name in old_security_records:
        cr.execute(
            """
            SELECT res_id
              FROM ir_model_data
             WHERE module = 'account_banking_mandate'
               AND model = %s
               AND name = %s
            """,
            (model, name),
        )
        res_ids = tuple(row[0] for row in cr.fetchall())
        if res_ids:
            cr.execute("SELECT to_regclass(%s)", (table,))
            if cr.fetchone()[0]:
                cr.execute(f"DELETE FROM {table} WHERE id IN %s", (res_ids,))
        cr.execute(
            """
            DELETE FROM ir_model_data
             WHERE module = 'account_banking_mandate'
               AND model = %s
               AND name = %s
            """,
            (model, name),
        )
