# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from openerp.osv import orm, fields


class account_move_line(orm.Model):

    """Account move line."""

    _inherit = 'account.move.line'
    _columns = {
        'draft_assigned': fields.boolean(
            'Draft Assigned',
            help=(
                "This field is checked when the move line is assigned "
                "to a draft deposit ticket. The deposit ticket is not "
                "still completely processed"
            ),
        ),
        'deposit_id': fields.many2one(
            'deposit.ticket',
            'Deposit Ticket'
        )
    }
