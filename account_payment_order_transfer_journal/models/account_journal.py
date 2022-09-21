# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountJournal(models.Model):

    _inherit = "account.journal"

    transfer_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Transfer journal on payment/debit orders",
        help="Journal to write payment entries when confirming payment/debit orders",
    )
