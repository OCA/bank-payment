# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def button_post(self):
        if self.env.company.account_prevent_reconcile_entry_post:
            self = self.with_context(dont_post_entry=True)
        super(AccountBankStatement, self).button_post()
