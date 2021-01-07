# Copyright 2013-2016 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class BankPaymentLine(models.Model):
    _inherit = "bank.payment.line"

    priority = fields.Selection(related="payment_line_ids.priority", string="Priority")
    local_instrument = fields.Selection(
        related="payment_line_ids.local_instrument", string="Local Instrument"
    )
    category_purpose = fields.Selection(
        related="payment_line_ids.category_purpose", string="Category Purpose"
    )
    purpose = fields.Selection(related="payment_line_ids.purpose")

    @api.model
    def same_fields_payment_line_and_bank_payment_line(self):
        res = super().same_fields_payment_line_and_bank_payment_line()
        res += ["priority", "local_instrument", "category_purpose", "purpose"]
        return res
