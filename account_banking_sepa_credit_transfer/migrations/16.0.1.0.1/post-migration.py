# Copyright 2023 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    sct_method = env.ref("account_banking_sepa_credit_transfer.sepa_credit_transfer")
    sct_method.write({"warn_not_sepa": True})
