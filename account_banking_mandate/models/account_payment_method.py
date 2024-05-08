# Copyright 2016-2020 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountPaymentMethod(models.Model):
    _inherit = "account.payment.method"

    mandate_required = fields.Boolean(
        help="Activate this option if this payment method requires your "
        "customer to sign a direct debit mandate with your company.",
    )

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res["sepa_direct_debit"] = {
            "mode": "multi",
            "domain": [("type", "=", "bank")],
        }
        return res
