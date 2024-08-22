# Copyright 2023 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    sdd_method = env.ref("account_banking_sepa_direct_debit.sepa_direct_debit")
    vals = {"payment_order_ok": True}
    if sdd_method.pain_version in ("pain.008.001.03", "pain.008.001.04"):
        vals["pain_version"] = "pain.008.001.02"
    sdd_method.write(vals)
