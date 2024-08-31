# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import ast

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"
    fs_storage_source_payment = fields.Selection(
        string="fs storage source payment",
        related="company_id.fs_storage_source_payment",
        readonly=False,
    )

    fs_storage_ids = fields.Many2many("fs.storage", string="Fs Storage allowed")

    @api.model
    def get_values(self):
        res = super().get_values()
        fs_storage_ids = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "account_payment_method_or_mode_fs_storage"
                f".fs_storage_ids_{self.env.company.id}"
            )
        )

        res.update(
            fs_storage_ids=[Command.set(ast.literal_eval(fs_storage_ids))]
            if fs_storage_ids
            else False
        )
        return res

    @api.model
    def set_values(self):
        self.env["ir.config_parameter"].sudo().set_param(
            f"account_payment_method_or_mode_fs_storage.fs_storage_ids_{self.env.company.id}",
            self.fs_storage_ids.ids,
        )
        return super().set_values()

    @api.constrains("fs_storage_ids")
    def _check_fs_storage_ids(self):
        fs_storage_source = self.fs_storage_source_payment
        if fs_storage_source == "mode":
            used_storages = (
                self.env["account.payment.mode"].search([]).mapped("storage")
            )
        else:
            used_storages = (
                self.env["account.payment.method"].search([]).mapped("storage")
            )
        if any(used_storages):
            ids = [int(storage_id) for storage_id in used_storages if storage_id]
            allowed_storages = self.fs_storage_ids
            if not set(allowed_storages.ids).issuperset([i for i in ids]):
                raise UserError(
                    _(
                        f"Storage is already used on at least one payment {fs_storage_source}"
                    )
                )
