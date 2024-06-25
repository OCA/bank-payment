# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _rename_modules(env):
    modules = [
        (
            "account_payment_method_fs_storage",
            "account_payment_method_or_mode_fs_storage",
        )
    ]
    openupgrade.update_module_names(env.cr, modules, merge_modules=True)


@openupgrade.migrate()
def migrate(env, version):
    _rename_modules(env)
