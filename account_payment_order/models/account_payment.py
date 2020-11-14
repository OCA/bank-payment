# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def _get_default_journal(self):
        res = super()._get_default_journal()
        return res.filtered(lambda journal: not journal.inbound_payment_order_only)

    @api.depends(
        "payment_type",
        "journal_id.inbound_payment_method_ids",
        "journal_id.outbound_payment_method_ids",
    )
    def _compute_payment_method_fields(self):
        res = super()._compute_payment_method_fields()
        for pay in self:
            if pay.payment_type == "inbound":
                pay.available_payment_method_ids = (
                    pay.journal_id.inbound_payment_method_ids.filtered(
                        lambda m: not m.payment_order_only
                    )
                )
            else:
                pay.available_payment_method_ids = (
                    pay.journal_id.outbound_payment_method_ids.filtered(
                        lambda m: not m.payment_order_only
                    )
                )

            pay.hide_payment_method = (
                len(pay.available_payment_method_ids) == 1
                and pay.available_payment_method_ids.code == "manual"
            )
        return res
