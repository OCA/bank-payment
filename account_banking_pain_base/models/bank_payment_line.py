# Copyright 2013-2022 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2021-2022 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class BankPaymentLine(models.Model):
    _inherit = "bank.payment.line"

    priority = fields.Selection(related="payment_line_ids.priority")
    local_instrument = fields.Selection(related="payment_line_ids.local_instrument")
    category_purpose_id = fields.Many2one(
        related="payment_line_ids.category_purpose_id"
    )
    purpose_id = fields.Many2one(related="payment_line_ids.purpose_id")

    @api.model
    def same_fields_payment_line_and_bank_payment_line(self):
        res = super().same_fields_payment_line_and_bank_payment_line()
        res += ["priority", "local_instrument", "category_purpose_id", "purpose_id"]
        return res
