# -*- coding: utf-8 -*-
# © 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    # Remove mandate bank view from partner banks. In v 9.0 the bank view has
    # been deleted from partner
    sql = """
        DELETE FROM ir_ui_view
        WHERE name = 'mandate.partner.form';
    """
    openupgrade.logged_query(env.cr, sql)
