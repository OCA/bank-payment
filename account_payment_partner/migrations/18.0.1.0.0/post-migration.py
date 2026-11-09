# Copyright 2025 Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade, openupgrade_180


@openupgrade.migrate()
def migrate(env, version):
    openupgrade_180.convert_company_dependent(
        env, "res.partner", "supplier_payment_mode_id"
    )
    openupgrade_180.convert_company_dependent(
        env, "res.partner", "customer_payment_mode_id"
    )
