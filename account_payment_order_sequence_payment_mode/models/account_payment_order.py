# © 2022 Acsone (<http://www.acsone.eu>))
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountPaymentOrder(models.Model):

    _inherit = "account.payment.order"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("payment_mode_id"):

                mode_id = vals.get("payment_mode_id")
                seq = (
                    self.env["account.payment.mode"]
                    .browse(mode_id)
                    .sequence_payment_order_id
                )
                if seq:

                    vals["name"] = seq._next()

        return super().create(vals_list)
