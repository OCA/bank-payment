# -*- coding: utf-8 -*-
# © 2013-2017 ACSONE SA (<http://acsone.eu>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    allow_direct_payment = fields.Boolean(
        help="But checking this option, you allow to use this journal through"
             " the Register Payment feature directly on an invoice",
        default=True
    )
