# Copyright 2024 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    def _set_payment_filename(self, filename):
        filename = super()._set_payment_filename(filename)

        if self.payment_mode_id.filename_sequence_id:
            filename = self._get_filename_with_sequence(filename)
        return filename

    def _get_filename_with_sequence(self, previous_filename=""):
        return self.payment_mode_id.filename_sequence_id._next() or previous_filename
