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


class add_deposit_items(orm.TransientModel):
    _name = "add.deposit.items"
    _description = "Add Deposit Items"
    _columns = {
        'name': fields.char(
            'Name',
            size=64
        ),
        'deposit_items_line_ids': fields.one2many(
            'deposit.items.line',
            'deposit_items_id',
            'Lines'
        ),
    }

    def default_get(self, cr, uid, fields, context=None):
        deposit_ticket_obj = self.pool.get('deposit.ticket')
        account_move_line_obj = self.pool.get('account.move.line')
        account_move = self.pool.get('account.move')
        result = []
        res = super(add_deposit_items, self).default_get(
            cr, uid, fields, context=context
        )
        deposits = deposit_ticket_obj.browse(
            cr, uid, context.get('active_ids', []), context=context
        )
        for deposit in deposits:
            # Filter all the move lines which are:
            # 1. Account.move.lines that are a member of the Deposit From
            #    GL Account and are Debits
            # 2. State of the move_id == Posted
            # 3. The Deposit Ticket # value is blank (null) not assigned
            # 4. The account move line is not a member of another Draft/To Be
            #    Review (this is the list (one2many) of
            #
            # debit transactions displayed on the selected Account (Undeposited
            # Funds Acct) including this account.
            move_ids = account_move.search(
                cr, uid, [('state', '=', 'posted')], context=context
            )
            line_ids = account_move_line_obj.search(
                cr, uid,
                [
                    ('account_id', '=', deposit.deposit_from_account_id.id),
                    ('debit', '>', 0.0),
                    ('move_id', 'in', move_ids),
                    ('draft_assigned', '=', False),
                    ('deposit_id', '=', False)
                ],
                context=context
            )
            lines = account_move_line_obj.browse(
                cr, uid, line_ids, context=context
            )
            for line in lines:
                result.append({
                    'name': line.name,
                    'ref': line.ref,
                    'amount': line.debit,
                    'partner_id': line.partner_id.id,
                    'date': line.date,
                    'move_line_id': line.id,
                    'company_id': line.company_id.id
                })

        if 'deposit_items_line_ids' in fields:
            res.update({'deposit_items_line_ids': result})
        return res

    def select_all(self, cr, uid, ids, context=None):
        """Select all the deposit item lines in the wizard."""
        deposit_items_line_obj = self.pool.get('deposit.items.line')
        deposit_ticket_item = self.browse(cr, uid, ids[0], context=context)
        line_ids = deposit_items_line_obj.search(
            cr, uid,
            [
                ('deposit_items_id', '=', deposit_ticket_item.id)
            ],
            context=context
        )
        deposit_items_line_obj.write(
            cr, uid, line_ids, {'draft_assigned': True}, context=context
        )
        return True

    def unselect_all(self, cr, uid, ids, context=None):
        """Unselect all the deposit item lines in the wizard."""
        deposit_items_line_obj = self.pool.get('deposit.items.line')
        deposit_ticket_item = self.browse(cr, uid, ids[0], context=context)
        line_ids = deposit_items_line_obj.search(
            cr, uid,
            [
                ('deposit_items_id', '=', deposit_ticket_item.id)
            ],
            context=context
        )
        deposit_items_line_obj.write(
            cr, uid, line_ids, {'draft_assigned': False}, context=context
        )
        return True

    def add_deposit_lines(self, cr, uid, ids, context=None):
        """Add Deposit Items Lines as Deposit Ticket Lines for the deposit."""
        deposit_ticket_obj = self.pool.get('deposit.ticket')
        account_move_line_obj = self.pool.get('account.move.line')
        deposit_ticket_line_obj = self.pool.get('deposit.ticket.line')
        deposit_ticket_item = self.browse(cr, uid, ids[0], context=context)
        deposits = deposit_ticket_obj.browse(
            cr, uid, context.get('active_ids', []), context=context
        )
        for deposit in deposits:
            # Add the deposit ticket item lines which have
            # 'draft_assigned' checked
            valid_items_line_ids = [
                line
                for line in deposit_ticket_item.deposit_items_line_ids
                if line.draft_assigned
            ]
            move_line_ids = []
            for line in valid_items_line_ids:
                # Any Line cannot be manually added.
                # Choose only from the selected lines.
                if not line.move_line_id:
                    raise orm.except_orm(
                        _('Processing Error'),
                        _(
                            'You cannot add any new deposit line item '
                            'manually as of this revision!'
                        )
                    )

                # Creating but not using the id of the new object anywhere
                deposit_ticket_line_obj.create(
                    cr, uid,
                    {
                        'name': line.name,
                        'ref': line.ref,
                        'amount': line.amount,
                        'partner_id': line.partner_id.id,
                        'date': line.date,
                        'move_line_id': line.move_line_id.id,
                        'company_id': line.company_id.id,
                        'deposit_id': deposit.id
                    },
                    context=context
                )

                move_line_ids.append(line.move_line_id.id)

            account_move_line_obj.write(
                cr, uid,
                move_line_ids,
                {
                    'draft_assigned': True
                },
                context=context
            )
        return {'type': 'ir.actions.act_window_close'}


class deposit_items_line(orm.TransientModel):
    _name = "deposit.items.line"
    _description = "Deposit Items Line"
    _columns = {
        'name': fields.char(
            'Name',
            size=64
        ),
        'ref': fields.char(
            'Reference',
            size=64
        ),
        'partner_id': fields.many2one(
            'res.partner',
            'Partner'
        ),
        'date': fields.date(
            'Date',
            required=True
        ),
        'amount': fields.float(
            'Amount',
            digits_compute=dp.get_precision('Account')
        ),
        'draft_assigned': fields.boolean('Select'),
        'deposit_items_id': fields.many2one(
            'add.deposit.items',
            'Deposit Items ID'
        ),
        'move_line_id': fields.many2one(
            'account.move.line',
            'Journal Item'
        ),
        'company_id': fields.many2one(
            'res.company',
            'Company'
        ),
    }
