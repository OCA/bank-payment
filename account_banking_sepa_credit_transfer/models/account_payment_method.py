# -*- coding: utf-8 -*-
# Copyright 2016-2020 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# Copyright 2026 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    pain_version = fields.Selection(
        selection_add=[
        ("pain.001.001.02", "pain.001.001.02"),
        ("pain.001.001.03", "pain.001.001.03"),
        ("pain.001.001.04", "pain.001.001.04"),
        ("pain.001.001.05", "pain.001.001.05"),
        ("pain.001.001.09", "pain.001.001.09 (recommended for credit transfer)"),
        ("pain.001.003.03", "pain.001.003.03"),
    ],
    )

    @api.multi
    def get_xsd_file_path(self):
        self.ensure_one()
        if self.pain_version in [
            "pain.001.001.02",
            "pain.001.001.03",
            "pain.001.001.04",
            "pain.001.001.05",
            "pain.001.001.09",
            "pain.001.003.03",
        ]:
            path = (
                "account_banking_sepa_credit_transfer/data/%s.xsd" % self.pain_version
            )
            return path
        return super(AccountPaymentMethod, self).get_xsd_file_path()
