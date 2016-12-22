# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    # Copy mandate_id to account_move_line
    sql = """
    UPDATE account_move_line aml
    SET mandate_id = ai.mandate_id
    FROM account_invoice ai
    WHERE aml.invoice_id=ai.id
    AND aml.invoice_id is not null
    AND ai.mandate_id is not null;
    """
    openupgrade.logged_query(env.cr, sql)
