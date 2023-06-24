# Copyright 2023 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountPaymentMode(models.Model):
    _inherit = "account.payment.mode"

    layout_id = fields.Many2one(comodel_name="account.payment.mode.layout")
