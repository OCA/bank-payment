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
from openerp.osv import fields, orm
from openerp.tools.translate import _
import decimal_precision as dp


class deposit_ticket_line(orm.Model):
    _name = "deposit.ticket.line"
    _description = "Deposit Ticket Line"
    _columns = {
        'name': fields.char(
            'Name',
            size=64,
            required=True,
            help="Derived from the related Journal Item."
        ),
        'ref': fields.char(
            'Reference',
            size=64,
            help="Derived from related Journal Item."
        ),
        'partner_id': fields.many2one(
            'res.partner',
            string='Partner',
            help="Derived from related Journal Item."
        ),
        'amount': fields.float(
            'Amount',
            digits_compute=dp.get_precision('Account'),
            help="Derived from the 'debit' amount from related Journal Item."
        ),
        'date': fields.date(
            'Date',
            required=True,
            help="Derived from related Journal Item."
        ),
        'deposit_id': fields.many2one(
            'deposit.ticket',
            'Deposit Ticket',
            required=True,
            ondelete='cascade'
        ),
        'company_id': fields.related(
            'deposit_id',
            'company_id',
            type='many2one',
            relation='res.company',
            string='Company',
            readonly=True,
            help="Derived from related Journal Item."
        ),
        'move_line_id': fields.many2one(
            'account.move.line',
            'Journal Item',
            help="Related Journal Item."
        ),
    }

    def create(self, cr, uid, vals, context=None):
        # Any Line cannot be manually added. Use the wizard to add lines.
        if not vals.get('move_line_id', False):
            raise orm.except_orm(
                _('Processing Error'),
                _(
                    'You cannot add any new deposit ticket line '
                    'manually as of this revision! '
                    'Please use the button "Add Deposit '
                    'Items" to add deposit ticket line!'
                )
            )
        return super(deposit_ticket_line, self).create(
            cr, uid, vals, context=context
        )

    def unlink(self, cr, uid, ids, context=None):
        """
        Set the 'draft_assigned' field to False for related account move
        lines to allow to be entered for another deposit.
        """
        account_move_line_obj = self.pool.get('account.move.line')
        move_line_ids = [
            line.move_line_id.id
            for line in self.browse(cr, uid, ids, context=context)
        ]
        account_move_line_obj.write(
            cr, uid, move_line_ids, {'draft_assigned': False}, context=context
        )
        return super(deposit_ticket_line, self).unlink(
            cr, uid, ids, context=context
        )
