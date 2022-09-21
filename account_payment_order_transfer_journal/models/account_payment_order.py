# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountPaymentOrder(models.Model):

    _inherit = "account.payment.order"

    def _prepare_move(self, bank_lines=None):
        res = super()._prepare_move(bank_lines=bank_lines)
        if self.journal_id.transfer_journal_id:
            res["journal_id"] = self.journal_id.transfer_journal_id.id
        return res
