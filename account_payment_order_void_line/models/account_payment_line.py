# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountPaymentLine(models.Model):
    _inherit = "account.payment.line"

    is_voided = fields.Boolean(string="Voided", default=False)
    void_date = fields.Date()
    void_reason = fields.Text()

    def call_payment_void_wizard(self):
        return {
            "name": ("Add a reason for cancel"),
            "view_mode": "form",
            "res_model": "cancel.void.payment.line",
            "view_id": False,
            "type": "ir.actions.act_window",
            "target": "new",
            # "context": {"mode": "entry"},
        }
