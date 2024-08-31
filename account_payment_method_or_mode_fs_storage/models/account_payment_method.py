# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import ast

from odoo import _, fields, models


class AccountPaymentMethod(models.Model):

    _inherit = "account.payment.method"

    storage = fields.Selection(
        selection="_get_selection_storage",
        default="",
        company_dependent=True,
        help="Storage where to put the file after generation",
    )

    def _get_selection_storage(self):
        """
        This is to avoid giving access to the model fs.storage
        at groups other than base.group_system
        """
        fs_storage_source = self.env.company.fs_storage_source_payment
        if fs_storage_source == "method":
            ids = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(
                    "account_payment_method_or_mode_fs_storage"
                    f".fs_storage_ids_{self.env.company.id}"
                )
            )
            if ids:
                storages = self.env["fs.storage"].browse(ast.literal_eval(ids))
                return [(str(r.id), r.display_name) for r in storages]
        else:
            # Return all available storage with a disabled notification
            storages = self.env["fs.storage"].search([])
            return [
                (str(r.id), r.display_name + _(" - disabled in mode payment setting"))
                for r in storages
            ]

        return []
