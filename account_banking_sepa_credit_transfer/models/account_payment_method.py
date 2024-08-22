# Copyright 2016-2020 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountPaymentMethod(models.Model):
    _inherit = "account.payment.method"

    pain_version = fields.Selection(
        selection_add=[
            (
                "pain.001.001.03",
                "pain.001.001.03 (credit transfer, old recommended version)",
            ),
            (
                "pain.001.001.09",
                "pain.001.001.09 (credit transfer, new recommended version)",
            ),
            ("pain.001.003.03", "pain.001.003.03 (credit transfer for Germany only)"),
        ],
        ondelete={
            "pain.001.001.03": "set null",
            "pain.001.001.09": "set null",
            "pain.001.003.03": "set null",
        },
    )

    def _get_xsd_file_path(self):
        self.ensure_one()
        if self.pain_version in [
            "pain.001.001.03",
            "pain.001.001.09",
            "pain.001.003.03",
        ]:
            path = (
                "account_banking_sepa_credit_transfer/data/%s.xsd" % self.pain_version
            )
            return path
        return super()._get_xsd_file_path()

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res["sepa_credit_transfer"] = {
            "mode": "multi",
            "domain": [("type", "=", "bank")],
        }
        return res
