# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class PaymentTransaction(models.Model):

    _inherit = 'payment.transaction'

    persistent_state_message = fields.Text(readonly=True)

    def _update_persistent_state_message(self):
        for transaction in self:
            persistent_state_message = transaction.persistent_state_message and transaction.persistent_state_message or ""
            if persistent_state_message:
                persistent_state_message += "\n"
            persistent_state_message += transaction.state_message
            transaction.write({
                "persistent_state_message": persistent_state_message,
            })

    def write(self, vals):
        res = super().write(vals)
        if "state_message" in vals and vals["state_message"] != "":
            self._update_persistent_state_message()
        return res
