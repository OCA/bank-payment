# Copyright 2023 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    if not version:
        return

    cr.execute(
        'ALTER TABLE "account_payment_method" RENAME "payment_order_only" '
        'TO "payment_order_ok"'
    )
    # Harmonize values for reference_type on account.move
    # and communication_type on account.payment.line:
    # 2 possible values : free and structured
    cr.execute(
        "UPDATE account_move SET reference_type='free' WHERE reference_type='none'"
    )
    cr.execute(
        "UPDATE account_payment_line SET communication_type='free' "
        "WHERE communication_type='normal'"
    )
    cr.execute(
        "UPDATE account_payment_line SET communication_type='structured' "
        "WHERE communication_type='ISO'"
    )
