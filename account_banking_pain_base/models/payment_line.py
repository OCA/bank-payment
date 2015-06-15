# -*- encoding: utf-8 -*-
##############################################################################
#
#    PAIN Base module for Odoo
#    Copyright (C) 2013-2015 Akretion (http://www.akretion.com)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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
