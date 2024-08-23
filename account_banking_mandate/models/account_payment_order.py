# Copyright 2024 Akretion France - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    mandate_required = fields.Boolean(related="payment_method_id.mandate_required")
