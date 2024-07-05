# Copyright 2024 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class AccountPaymentMode(models.Model):
    _inherit = "account.payment.mode"

    filename_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        help="Sequence used to generate the filename",
    )
