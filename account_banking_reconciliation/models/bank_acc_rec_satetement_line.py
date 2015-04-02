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
import openerp.addons.decimal_precision as dp


class bank_acc_rec_statement_line(orm.Model):
    _name = "bank.acc.rec.statement.line"
    _description = "Statement Line"
    _columns = {
        'name': fields.char(
            'Name',
            size=64,
            help="Derived from the related Journal Item.",
            required=True
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
        'amount_in_currency': fields.float(
            'Amount in Currency',
            digits_compute=dp.get_precision('Account'),
            help="Amount in currency from the related Journal Item."
        ),
        'date': fields.date(
            'Date',
            required=True,
            help="Derived from related Journal Item."
        ),
        'statement_id': fields.many2one(
            'bank.acc.rec.statement',
            'Statement',
            required=True,
            ondelete='cascade'
        ),
        'move_line_id': fields.many2one(
            'account.move.line',
            'Journal Item',
            help="Related Journal Item."
        ),
        'cleared_bank_account': fields.boolean(
            'Cleared ',
            help='Check if the transaction has cleared from the bank'
        ),
        'research_required': fields.boolean(
            'Research Required ',
            help=(
                'Check if the transaction should be researched by '
                'Accounting personal'
            ),
        ),
        'currency_id': fields.many2one(
            'res.currency',
            'Currency',
            help="The optional other currency if it is a multi-currency entry."
        ),
        'type': fields.selection(
            [
                ('dr', 'Debit'),
                ('cr', 'Credit')
            ],
            'Cr/Dr'
        ),
    }

    def create(self, cr, uid, vals, context=None):
        account_move_line_obj = self.pool.get('account.move.line')
        # Prevent manually adding new statement line.
        # This would allow only onchange method to pre-populate
        # statement lines based on the filter rules.
        if not vals.get('move_line_id', False):
            raise orm.except_orm(
                _('Processing Error'),
                _('You cannot add any new bank statement line '
                  'manually as of this revision!')
            )
        account_move_line_obj.write(
            cr, uid,
            [vals['move_line_id']],
            {'draft_assigned_to_statement': True},
            context=context
        )
        return super(bank_acc_rec_statement_line, self).create(
            cr, uid, vals, context=context
        )

    def unlink(self, cr, uid, ids, context=None):
        account_move_line_obj = self.pool.get('account.move.line')
        move_line_ids = [
            line.move_line_id.id
            for line in self.browse(cr, uid, ids, context=context)
            if line.move_line_id
        ]
        # Reset field values in move lines to be added later
        account_move_line_obj.write(
            cr, uid,
            move_line_ids,
            {
                'draft_assigned_to_statement': False,
                'cleared_bank_account': False,
                'bank_acc_rec_statement_id': False,
            },
            context=context
        )
        return super(bank_acc_rec_statement_line, self).unlink(
            cr, uid, ids, context=context
        )
