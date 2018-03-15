# -*- coding: utf-8 -*-
# Copyright 2018 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountPaymentMode(models.Model):
    _inherit = 'account.payment.mode'

    show_bank_account = fields.Selection(
        selection=[
            ('full', 'Full'),
            ('first', 'First n chars'),
            ('last', 'Last n chars'),
            ('no', 'No'),
        ],
        string='Show bank account',
        default='full',
        help="Show in invoices partial or full bank account number")
    show_bank_account_from_journal = fields.Boolean(
        string='Bank account from journals'
    )
    show_bank_account_chars = fields.Integer(
        string="# of digits for customer bank account",
    )
