# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 - 2014 Therp BV (<http://therp.nl>).
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
from openerp.osv import orm


class ResBank(orm.Model):
    _inherit = 'res.bank'

    def online_account_info(
            self, cr, uid, country_code, acc_number, context=None):
        """
        API hook for legacy online lookup of account info, 
        to be removed in OpenERP 8.0.
        """
        return False
