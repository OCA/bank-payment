# -*- encoding: utf-8 -*-
##############################################################################
#
#    PAIN Base module for Odoo
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
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

from openerp import SUPERUSER_ID


def set_default_initiating_party(cr, pool):
    company_ids = pool['res.company'].search(cr, SUPERUSER_ID, [])
    companies = pool['res.company'].browse(cr, SUPERUSER_ID, company_ids)
    for company in companies:
        pool['res.company']._default_initiating_party(
            cr, SUPERUSER_ID, company)
    return
