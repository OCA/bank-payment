# Copyright 2022 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade
from psycopg2 import sql

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    iclo = env["iso20022.code.list"].with_context(active_test=False)
    for field_name in ["purpose", "category_purpose"]:
        code2id = {}
        for codelist in iclo.search_read([("field", "=", field_name)], ["code"]):
            code2id[codelist["code"]] = codelist["id"]

        legacy_field_name = openupgrade.get_legacy_name(field_name)

        select = sql.SQL("SELECT distinct({}) FROM account_payment_line").format(
            sql.Identifier(legacy_field_name)
        )
        openupgrade.logged_query(env.cr, select)
        for res in cr.fetchall():
            code = res[0]
            codelist_id = code2id.get(code)
            if codelist_id:
                update = sql.SQL(
                    "UPDATE account_payment_line SET {}=%s WHERE {}=%s"
                ).format(
                    sql.Identifier("%s_id" % field_name),
                    sql.Identifier(legacy_field_name),
                )
                openupgrade.logged_query(env.cr, update, (codelist_id, code))
