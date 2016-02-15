# -*- coding: utf-8 -*-
# © 2014 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class PaymentMode(models.Model):
    _inherit = "payment.mode"

    label = fields.Char(
        string='Label', translate=True,
        help="This field is designed to be used in the invoice report")
    default_payment_mode = fields.Selection([
        ('same', 'Same'),
        ('same_or_null', 'Same or empty'),
        ('any', 'Any'),
        ], string='Payment Mode on Invoice', default='same')
