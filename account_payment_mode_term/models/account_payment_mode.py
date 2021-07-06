# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class AccountPaymentMode(models.Model):
    _inherit = "account.payment.mode"

    payment_term_ids = fields.Many2many(
        comodel_name="account.payment.term",
        relation="account_payment_mode_terms_rel",
        column1="account_payment_mode_id",
        column2="account_payment_term_id",
        string="Payment terms",
        help="Limit selected invoices to invoices with these payment terms",
    )
