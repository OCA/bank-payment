# Copyright 2023 Noviat - Luc De Meyer
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    payments = env["account.payment"].search([])
    for payment in payments:
        if payment.ref == payment.payment_order_id.name:
            payment.ref = " - ".join(
                [line.communication for line in payment.payment_line_ids]
            )
