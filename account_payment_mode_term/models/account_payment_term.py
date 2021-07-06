# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    payment_mode_ids = fields.Many2many(
        comodel_name="account.payment.mode",
        relation="account_payment_mode_terms_rel",
        column1="account_payment_term_id",
        column2="account_payment_mode_id",
        string="Payment Modes",
        readonly=True,
    )
