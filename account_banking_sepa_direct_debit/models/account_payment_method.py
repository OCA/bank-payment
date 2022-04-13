# Copyright 2020 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountPaymentMethod(models.Model):
    _inherit = "account.payment.method"

    pain_version = fields.Selection(
        selection_add=[
            ("pain.008.001.02", "pain.008.001.02 (recommended for direct debit)"),
            ("pain.008.001.03", "pain.008.001.03"),
            ("pain.008.001.04", "pain.008.001.04"),
            ("pain.008.003.02", "pain.008.003.02 (direct debit in Germany)"),
        ],
        ondelete={
            "pain.008.001.02": "set null",
            "pain.008.001.03": "set null",
            "pain.008.001.04": "set null",
            "pain.008.003.02": "set null",
        },
    )

    def get_xsd_file_path(self):
        self.ensure_one()
        if self.pain_version in [
            "pain.008.001.02",
            "pain.008.001.03",
            "pain.008.001.04",
            "pain.008.003.02",
        ]:
            path = "account_banking_sepa_direct_debit/data/%s.xsd" % self.pain_version
            return path
        return super().get_xsd_file_path()

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res["sepa_direct_debit"] = {"mode": "multi", "domain": [("type", "=", "bank")]}
        return res
