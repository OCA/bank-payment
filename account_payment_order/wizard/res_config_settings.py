# Copyright 2023 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    transfer_journal_id = fields.Many2one(
        related="company_id.transfer_journal_id", readonly=False
    )
