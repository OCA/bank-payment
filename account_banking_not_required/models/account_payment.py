# -*- coding: utf-8 -*-

from openerp import models, fields, api

class account_banking_not_required(models.Model):
    _inherit = 'payment.mode'

    bank_id = fields.Many2one(required=False)
    check_required = fields.Boolean(default=True,
    string="Bank account required",
    help="This check do bank account optional for payment mode that isn't necessary to inform")
