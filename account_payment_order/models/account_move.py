# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_order_id = fields.Many2one(
        'account.payment.order', string='Payment Order', copy=False,
        readonly=True)
