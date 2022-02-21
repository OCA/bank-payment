# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade  # pylint: disable=W7936


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET payment_mode_id = ai.payment_mode_id
        FROM account_invoice ai
        WHERE ai.id = am.old_invoice_id""",
    )
    # Fill new move lines created from draft/cancel invoices in account module with the
    # proper payment mode following the logic in the compute method
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line aml
        SET payment_mode_id = am.payment_mode_id
        FROM account_move am
        WHERE am.id = aml.move_id
            AND am.type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund')
            AND aml.account_internal_type in ('receivable', 'payable')
            AND aml.payment_mode_id IS NULL AND am.payment_mode_id IS NOT NULL""",
    )
