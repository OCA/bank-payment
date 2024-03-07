# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class FsStorage(models.Model):

    _inherit = "fs.storage"

    use_on_payment_method = fields.Boolean(
        help="Tells if storage can be set on payment methods",
    )

    @api.constrains("use_on_payment_method")
    def _check_use_on_payment_method(self):
        storage_not_on_payment = self.filtered(lambda r: not r.use_on_payment_method)
        storage_not_on_payment_str_ids = [str(r.id) for r in storage_not_on_payment]
        data = self.env["account.payment.method"].read_group(
            domain=[("storage", "in", storage_not_on_payment_str_ids)],
            fields=["storage"],
            groupby=["storage"],
        )
        mapped_data = {r["storage"]: r["storage_count"] for r in data}

        if any(mapped_data.get(str(rec.id), 0) > 0 for rec in storage_not_on_payment):
            raise UserError(_("Storage is already used on at least one payment method"))
