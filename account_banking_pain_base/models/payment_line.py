# -*- coding: utf-8 -*-
# © 2013-2015 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class PaymentLine(models.Model):
    _inherit = 'payment.line'

    @api.model
    def _get_struct_communication_types(self):
        return [('ISO', 'ISO')]

    priority = fields.Selection([
        ('NORM', 'Normal'),
        ('HIGH', 'High')],
        string='Priority', default='NORM',
        help="This field will be used as the 'Instruction Priority' in "
             "the generated PAIN file.")
    # Update size from 64 to 140, because PAIN allows 140 caracters
    communication = fields.Char(size=140)
    struct_communication_type = fields.Selection(
        '_get_struct_communication_types',
        string='Structured Communication Type', default='ISO')
