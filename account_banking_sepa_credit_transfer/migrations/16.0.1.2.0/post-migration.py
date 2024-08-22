# Copyright 2023 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    sct_method = env.ref("account_banking_sepa_credit_transfer.sepa_credit_transfer")
    vals = {"payment_order_ok": True}
    if sct_method.pain_version in (
        "pain.001.001.02",
        "pain.001.001.04",
        "pain.001.001.05",
    ):
        vals["pain_version"] = "pain.001.001.03"
    sct_method.write(vals)
