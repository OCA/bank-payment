# Copyright 2024 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    transfer_payable_account_id = fields.Many2one(
        comodel_name="account.account",
        domain="[('internal_type', '=', 'payable'), ('company_id', '=', company_id)]",
        string="Internal Transfer Payable Account",
    )
    transfer_receivable_account_id = fields.Many2one(
        comodel_name="account.account",
        domain="[('internal_type', '=', 'receivable'), ('company_id', '=', company_id)]",
        string="Internal Transfer Receivable Account",
    )
