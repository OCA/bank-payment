# Copyright 2016-2020 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def _default_outbound_payment_methods(self):
        all_out = self.env["account.payment.method"].search(
            [("payment_type", "=", "outbound")]
        )
        return all_out

    def _default_inbound_payment_methods(self):
        method_info = self.env[
            "account.payment.method"
        ]._get_payment_method_information()
        unique_codes = tuple(
            code for code, info in method_info.items() if info.get("mode") == "unique"
        )
        all_in = self.env["account.payment.method"].search(
            [
                ("payment_type", "=", "inbound"),
                ("code", "not in", unique_codes),  # filter out unique codes
            ]
        )
        return all_in
