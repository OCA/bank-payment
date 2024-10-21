# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class AccountPaymentMode(models.Model):

    _inherit = "account.payment.mode"

    default_receivable_account_id = fields.Many2one(
        "account.account",
        domain="[('deprecated', '=', False),('company_id', '=', company_id),('account_type', '=', 'asset_receivable')]",  # noqa
        help="This account will be used instead of the default one as the receivable account on invoices using this payment mode",  # noqa
    )
    default_payable_account_id = fields.Many2one(
        "account.account",
        domain="[('deprecated', '=', False), ('company_id', '=', company_id),('account_type', '=', 'liability_payable')]",  # noqa
        help="This account will be used instead of the default one as the payable account on invoices using this payment mode",  # noqa
    )
