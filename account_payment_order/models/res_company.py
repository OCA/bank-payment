# Copyright 2023 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    transfer_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Transfer journal on payment/debit orders",
        domain="[('type', '=', 'general')]",
        help="Journal to write payment entries when confirming payment/debit orders",
    )
