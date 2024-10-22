# Copyright 2024 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    transfer_payable_account_id = fields.Many2one(
        comodel_name="account.account",
        related="company_id.transfer_payable_account_id",
        string="Internal Transfer Payable Account",
        readonly=False,
    )
    transfer_receivable_account_id = fields.Many2one(
        comodel_name="account.account",
        related="company_id.transfer_receivable_account_id",
        string="Internal Transfer Receivable Account",
        readonly=False,
    )
