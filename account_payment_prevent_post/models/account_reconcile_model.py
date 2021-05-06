# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models


class AccountReconcileModel(models.Model):
    _inherit = "account.reconcile.model"

    def _apply_rules(self, st_lines, excluded_ids=None, partner_map=None):
        self = self.with_context(dont_post_entry=True)
        results = super(AccountReconcileModel, self)._apply_rules(
            st_lines, excluded_ids, partner_map
        )
        return results
