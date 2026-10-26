# Copyright 2023 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    transfer_journal_id = fields.Many2one(
        related="company_id.transfer_journal_id", readonly=False
    )
    use_allow_out_payment = fields.Boolean(
        string=" Use allow out payment on partner bank",
        config_parameter=("account_payment_order.use_allow_out_payment"),
    )
