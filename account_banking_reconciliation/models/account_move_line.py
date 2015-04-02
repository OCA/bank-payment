# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
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
from openerp.osv import fields, orm


class account_move_line(orm.Model):
    _inherit = 'account.move.line'

    _columns = {
        'cleared_bank_account': fields.boolean(
            'Cleared ',
            help='Check if the transaction has cleared from the bank'
        ),
        'bank_acc_rec_statement_id': fields.many2one(
            'bank.acc.rec.statement',
            'Bank Acc Rec Statement',
            help="The Bank Acc Rec Statement linked with the journal item"
        ),
        'draft_assigned_to_statement': fields.boolean(
            'Assigned to Statement ',
            help='Check if the move line is assigned to statement lines'
        )
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}

        default.update(
            cleared_bank_account=False,
            bank_acc_rec_statement_id=False,
            draft_assigned_to_statement=False,
        )

        return super(account_move_line, self).copy_data(
            cr, uid, id, default=default, context=context
        )
