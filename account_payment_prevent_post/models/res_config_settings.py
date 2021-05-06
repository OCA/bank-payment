# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    account_prevent_payment_entry_post = fields.Boolean(
        related="company_id.account_prevent_payment_entry_post",
        string="Prevent payment entry post",
        readonly=False,
        help="This option allows you to prevent autopost on Register payment.",
    )
    account_prevent_bank_st_entry_post = fields.Boolean(
        related="company_id.account_prevent_bank_st_entry_post",
        string="Prevent bank statement entry post",
        readonly=False,
        help="This option allows you to prevent autopost on Bank statement post.",
    )
