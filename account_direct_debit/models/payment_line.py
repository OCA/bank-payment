# -*- coding: utf-8 -*-
from openerp import models, fields


class PaymentLine(models.Model):
    _inherit = 'payment.line'

    # The original string is "Destination Bank Account"...
    # but in direct debit this field is the *Source* Bank Account !
    bank_id = fields.Many2one(string='Partner Bank Account')
