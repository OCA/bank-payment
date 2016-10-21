# -*- coding: utf-8 -*-
# © 2011 Smile (<http://smile.fr>)
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class PaymentLine(models.Model):
    _inherit = 'payment.line'

    # The original string is "Destination Bank Account"...
    # but in direct debit this field is the *Source* Bank Account !
    bank_id = fields.Many2one(string='Partner Bank Account')
