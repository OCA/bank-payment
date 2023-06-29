# Copyright 2023 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountPaymentLine(models.Model):
    _inherit = "account.payment.line"

    def _prepare_account_payment_vals(self):
        vals = super()._prepare_account_payment_vals()
        if self.order_id.journal_id.transfer_journal_id:
            vals["journal_id"] = self.order_id.journal_id.transfer_journal_id.id
        return vals
