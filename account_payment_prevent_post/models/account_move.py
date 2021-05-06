# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_register_payment(self):
        res = super(AccountMove, self).action_register_payment()
        if res.get("context"):
            if self.env.company.account_prevent_payment_entry_post:
                res["context"].update({"dont_post_entry": True})
        return res

    def _post(self, soft=True):
        context = self._context or {}
        if context.get("dont_post_entry"):
            return self
        return super(AccountMove, self)._post(soft=False)
