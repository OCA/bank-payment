# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    fields_mapping = [
        ("property_account_receivable_id", "property_stored_account_receivable_id"),
        ("property_account_payable_id", "property_stored_account_payable_id"),
    ]
    for orig_fname, new_fname in fields_mapping:
        orig_model_field = env["ir.model.fields"]._get("res.partner", orig_fname)
        new_model_field = env["ir.model.fields"]._get("res.partner", new_fname)
        sql = """
            UPDATE ir_property
            SET name = %s,
            fields_id = %s
            WHERE fields_id = %s;
        """
        cr.execute(sql, (new_fname, new_model_field.id, orig_model_field.id))


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    fields_mapping = [
        ("property_account_receivable_id", "property_stored_account_receivable_id"),
        ("property_account_payable_id", "property_stored_account_payable_id"),
    ]
    for orig_fname, new_fname in fields_mapping:
        orig_model_field = env["ir.model.fields"]._get("res.partner", orig_fname)
        new_model_field = env["ir.model.fields"]._get("res.partner", new_fname)
        sql = """
            UPDATE ir_property
            SET name = %s,
            fields_id = %s
            WHERE fields_id = %s;
        """
        cr.execute(sql, (orig_fname, orig_model_field.id, new_model_field.id))
