# -*- coding: utf-8 -*-
# © 2013-2017 ACSONE SA (<http://acsone.eu>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        res = super(AccountPayment, self)._onchange_payment_type()
        res['domain']['journal_id'].append(('allow_direct_payment', '=', True))
        return res
