# -*- coding: utf-8 -*-
# © 2013-2015 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class PaymentMode(models.Model):
    _inherit = 'payment.mode'

    convert_to_ascii = fields.Boolean(
        string='Convert to ASCII', default=True,
        help="If active, Odoo will convert each accented caracter to "
        "the corresponding unaccented caracter, so that only ASCII "
        "caracters are used in the generated PAIN file.")
