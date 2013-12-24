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


class payment_mode(orm.Model):
    _inherit = 'payment.mode'

    _columns = {
        'convert_to_ascii': fields.boolean(
            'Convert to ASCII',
            help="If active, OpenERP will convert each accented caracter to "
            "the corresponding unaccented caracter, so that only ASCII "
            "caracters are used in the generated PAIN file."),
    }

    _defaults = {
        'convert_to_ascii': True,
    }
