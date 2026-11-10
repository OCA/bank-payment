# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountPaymentLine(models.Model):
    _inherit = "account.payment.line"

    @api.model_create_multi
    def create(self, vals_list):
        order_ids = {vals.get("order_id") for vals in vals_list} - {None, False}
        self.env["account.payment.order"].browse(
            list(order_ids)
        )._api_check_lines_editable()
        return super().create(vals_list)

    def write(self, vals):
        (
            self.order_id | self.order_id.browse(vals.get("order_id") or ())
        )._api_check_lines_editable()
        return super().write(vals)

    def unlink(self):
        self.order_id._api_check_lines_editable()
        return super().unlink()
