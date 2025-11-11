# Copyright 2026 Therp BV (https://therp.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env["account.payment.method"].search(
        [
            ("payment_type", "=", "outbound"),
            ("code", "=", "sepa_credit_transfer"),
            ("pain_version", "=", "pain.001.001.03"),
        ]
    ).write({"pain_version": "pain.001.001.09"})
