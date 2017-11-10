# -*- coding: utf-8 -*-
# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return
    # Force recompute acc_type, issue with inheritance chain between base
    # module and base_iban with this module
    if openupgrade.is_module_installed(env.cr, 'base_iban'):
        env['res.partner.bank'].search([])._compute_acc_type()
