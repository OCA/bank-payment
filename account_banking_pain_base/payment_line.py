# -*- encoding: utf-8 -*-
##############################################################################
#
#    PAIN Base module for OpenERP
#    Copyright (C) 2013 Akretion (http://www.akretion.com)
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

from openerp.osv import orm, fields


class payment_line(orm.Model):
    _inherit = 'payment.line'

    def _get_struct_communication_types(self, cr, uid, context=None):
        return [('ISO', 'ISO')]

    _columns = {
        'priority': fields.selection(
            [
                ('NORM', 'Normal'),
                ('HIGH', 'High'),
            ],
            'Priority',
            help="This field will be used as the 'Instruction Priority' in "
            "the generated PAIN file."),
        # Update size from 64 to 140, because PAIN allows 140 caracters
        'communication': fields.char(
            'Communication', size=140, required=True,
            help="Used as the message between ordering customer and current "
            "company. Depicts 'What do you want to say to the recipient "
            "about this order ?'"),
        'struct_communication_type': fields.selection(
            _get_struct_communication_types, 'Structured Communication Type'),
    }

    _defaults = {
        'priority': 'NORM',
        'struct_communication_type': 'ISO',
    }
