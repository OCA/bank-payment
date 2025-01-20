# Copyright 2024-2025 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    bank_account_required = fields.Boolean(
        related="preferred_payment_method_line_id.payment_method_id.bank_account_required",
    )
    payment_method_code = fields.Char(
        related="preferred_payment_method_line_id.payment_method_id.code", store=True
    )
