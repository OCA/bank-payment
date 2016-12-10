# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openupgradelib import openupgrade


def migrate(cr, version):
    """Copy convert_to_ascii to account_payment_method."""
    sql = """
    UPDATE account_payment_method p_method
    SET convert_to_ascii=p_mode.%s
    FROM account_payment_mode p_mode
    WHERE p_mode.payment_method_id=p_method.id
    """ % openupgrade.get_legacy_name('convert_to_ascii')
    openupgrade.logged_query(cr, sql)
