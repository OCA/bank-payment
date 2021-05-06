# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    account_prevent_payment_entry_post = fields.Boolean()
    account_prevent_bank_st_entry_post = fields.Boolean()
