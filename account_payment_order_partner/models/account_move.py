# Copyright (C) 2021, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _prepare_new_payment_order(self, payment_mode=None):
        res = super()._prepare_new_payment_order()
        if self._context.get("is_pyo_as_per_customer"):
            res.update({"partner_id": self.partner_id.id})
        if self._context.get("is_new_order"):
            res.update({"state": "new"})
        return res

    def get_account_payment_domain(self, payment_mode):
        domain = [("payment_mode_id", "=", payment_mode.id)]
        if self._context.get("is_new_order"):
            domain.append(("state", "=", "new"))
        else:
            domain.append(("state", "=", "draft"))
        if self._context.get("is_pyo_as_per_customer"):
            domain.append(("partner_id", "=", self.partner_id.id))
        return domain

    def create_account_payment_line_new(self):
        return self.create_account_payment_line()
