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
import time

from openerp.osv import fields, orm
from openerp.tools.translate import _
import decimal_precision as dp


class deposit_ticket(orm.Model):
    _name = "deposit.ticket"
    _description = "Deposit Ticket"

    def check_group(self, cr, uid, ids, context=None):
        """
        Check if following security constraints are implemented for groups:
        Make Deposits Preparer - they can create, view and delete any of the
        Deposit Tickets provided the Deposit Ticket is not in the DONE state,

        or the Ready for Review state.
        Make Deposits Verifier - they can create, view, edit, and delete any of
        the Deposits Tickets information at any time.
        NOTE: DONE Deposit Tickets are only allowed to be deleted by a
        Make Deposits Verifier.
        """
        model_data_obj = self.pool.get('ir.model.data')
        res_groups_obj = self.pool.get('res.groups')
        group_verifier_id = model_data_obj._get_id(
            cr, uid,
            'account_banking_make_deposit', 'group_make_deposits_verifier'
        )
        for deposit in self.browse(cr, uid, ids, context=context):
            if group_verifier_id:
                res_id = model_data_obj.read(
                    cr, uid, [group_verifier_id], ['res_id']
                )[0]['res_id']

                group_verifier = res_groups_obj.browse(
                    cr, uid, res_id, context=context
                )
                group_user_ids = [user.id for user in group_verifier.users]
                if deposit.state != 'draft' and uid not in group_user_ids:
                    raise orm.except_orm(
                        _('User Error'),
                        _(
                            "Only a member of '%s' group may delete/edit "
                            "deposit tickets when not in draft state!" %
                            (group_verifier.name)
                        )
                    )
        return True

    def unlink(self, cr, uid, ids, context=None):
        # Check if the user is allowed to perform the action
        self.check_group(cr, uid, ids, context)
        # Call the method necessary to remove the changes made earlier
        self.remove_all(cr, uid, ids, context=context)
        return super(deposit_ticket, self).unlink(
            cr, uid, ids, context=context
        )

    def write(self, cr, uid, ids, vals, context=None):
        # Check if the user is allowed to perform the action
        self.check_group(cr, uid, ids, context)
        return super(deposit_ticket, self).write(
            cr, uid, ids, vals, context=context
        )

    def action_cancel(self, cr, uid, ids, context=None):
        # Call the method necessary to remove the changes made earlier
        self.remove_all(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        return True

    def action_review(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {
            'state': 'to_be_reviewed',
            'prepared_by_user_id': uid
        }, context=context)
        return True

    def action_process(self, cr, uid, ids, context=None):
        """
        Do the following:
        1.The 'Verifier By'  field is populated by the name of the Verifier.
        2.The 'Deposit Ticket #' field is populated.
        3.The account.move.lines are updated and written with
          the 'Deposit Ticket #'
        4.The status field is updated to "Done"
        5.New GL entries are made.
        """
        move_lines = []
        for deposit in self.browse(cr, uid, ids, context=context):
            if not deposit.journal_id.sequence_id:
                raise orm.except_orm(
                    _('Error'),
                    _('Please define sequence on deposit journal')
                )
            if deposit.journal_id.centralisation:
                raise orm.except_orm(
                    _('User Error'),
                    _('Cannot create move on centralised journal')
                )
            # Create the move lines first
            move_lines.append(
                (0, 0, self.get_move_line(cr, uid, deposit, 'src'))
            )
            move_lines.append(
                (0, 0, self.get_move_line(cr, uid, deposit, 'dest'))
            )
            # Create the move for the deposit
            move = {
                'ref': deposit.deposit_bag_no,
                'name': '/',
                'line_id': move_lines,
                'journal_id': deposit.journal_id.id,
                'date': deposit.date,
                'narration': deposit.deposit_bag_no,
                'deposit_id': deposit.id
            }
            move_id = self.pool.get('account.move').create(
                cr, uid, move, context=context
            )
            # Post the account move
            self.pool.get('account.move').post(cr, uid, [move_id])
            # Link the move with the deposit and populate other fields
            self.write(cr, uid, [deposit.id], {
                'move_id': move_id,
                'state': 'done',
                'verified_by_user_id': uid,
                'verified_date': time.strftime('%Y-%m-%d')
            }, context=context)

        return True

    def get_move_line(self, cr, uid, deposit, type, context=None):
        return {
            'type': type,
            'name': deposit.name or '/',
            'debit': type == 'dest' and deposit.amount or 0.0,
            'credit': type == 'src' and deposit.amount or 0.0,
            'account_id': (
                type == 'src' and
                deposit.deposit_from_account_id.id or
                deposit.deposit_to_account_id.id
            ),
            'date': deposit.date,
            'ref': deposit.deposit_bag_no or '',
            'deposit_id': deposit.id
        }

    def remove_all(self, cr, uid, ids, context=None):
        """
        Reset the deposit ticket to draft state,
        and remove the entries associated with the DONE transactions (
        account moves, updating account.move.lines, resetting preparer
        and verifier and verified date fields.
        Reflect all changes necessary.
        """
        account_move_line_obj = self.pool.get('account.move.line')
        account_move_obj = self.pool.get('account.move')
        move_line_ids = []
        vals = {
            'draft_assigned': False,
            'deposit_id': False
        }
        for deposit in self.browse(cr, uid, ids, context=context):
            move_line_ids = map(lambda x: x.move_line_id.id,
                                deposit.ticket_line_ids)
            if deposit.move_id:
                # Cancel the posted account move
                account_move_obj.button_cancel(
                    cr, uid, [deposit.move_id.id], context=context
                )
                # Finally, delete the account move
                account_move_obj.unlink(
                    cr, uid, [deposit.move_id.id], context=context
                )
                vals['draft_assigned'] = True

        account_move_line_obj.write(
            cr, uid, move_line_ids, vals, context=context
        )
        return True

    def action_cancel_draft(self, cr, uid, ids, context=None):
        # Call the method necessary to remove the changes made earlier
        self.remove_all(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {
            'state': 'draft',
            'verified_by_user_id': False,
            'verified_date': False,
            'prepared_by_user_id': False
        }, context=context)
        return True

    def _get_period(self, cr, uid, context=None):
        periods = self.pool.get('account.period').find(cr, uid)
        return periods and periods[0] or False

    def _get_amount(self, cr, uid, ids, name, args, context=None):
        res = {}
        for deposit in self.browse(cr, uid, ids, context=context):
            sum = 0.0
            for line in deposit.ticket_line_ids:
                sum += line.amount
            res[deposit.id] = sum
        return res

    def _get_count_total(self, cr, uid, ids, name, args, context=None):
        res = {}
        for deposit in self.browse(cr, uid, ids, context=context):
            res[deposit.id] = len(deposit.ticket_line_ids)
        return res

    def get_deposit_states(self, cr, uid, context=None):
        return [
            ('draft', _('Draft')),
            ('to_be_reviewed', _('Ready for Review')),
            ('done', _('Done')),
            ('cancel', _('Cancel')),
        ]

    def get_state(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]

        assert len(ids) == 1, 'Expected one record'

        deposit = self.browse(cr, uid, ids[0], context=context)

        states = {
            s[0]: s[1] for s in
            self.get_deposit_states(cr, uid, context=context)
        }

        return states[deposit.state]

    _columns = {
        'memo': fields.char(
            'Memo',
            size=64,
            states={'done': [('readonly', True)]},
            help="Memo for the deposit ticket",
        ),
        'deposit_to_account_id': fields.many2one(
            'account.account',
            'Deposit To Acct',
            required=True,
            states={'done': [('readonly', True)]},
            domain="[('company_id', '=', company_id), ('type', '!=', 'view')]",
            help="The Bank/Gl Account the Deposit is being made to.",
        ),
        'deposit_from_account_id': fields.many2one(
            'account.account',
            'Deposit From Acct',
            required=True,
            states={'done': [('readonly', True)]},
            domain="[('company_id', '=', company_id), ('type', '!=', 'view')]",
            help="The Bank/GL Account the Payments are currently found in.",
        ),
        'date': fields.date(
            'Date of Deposit',
            required=True,
            states={'done': [('readonly', True)]},
            help="The Date of the Deposit Ticket."
        ),
        'journal_id': fields.many2one(
            'account.journal',
            'Journal',
            required=True,
            states={'done': [('readonly', True)]},
            help="The Journal to hold accounting entries."
        ),
        'company_id': fields.many2one(
            'res.company',
            'Company',
            required=True,
            readonly=True,
            help="The Company for which the deposit ticket is made to"
        ),
        'period_id': fields.many2one(
            'account.period',
            'Force Period',
            required=True,
            states={'done': [('readonly', True)]},
            help="The period used for the accounting entries.",
        ),
        'deposit_method_id': fields.many2one(
            'deposit.method',
            'Deposit Method',
            states={'done': [('readonly', True)]},
            help=(
                "This is how the deposit was made: Examples: "
                "*Teller \n"
                "*ATM \n"
                "*Remote Deposit Capture \n"
                "*Online Deposit Capture \n"
                "*Night Drop"
            )
        ),
        'verified_date': fields.date(
            'Verified Date',
            states={'done': [('readonly', True)]},
            help="Date in which Deposit Ticket was verified."
        ),
        'prepared_by_user_id': fields.many2one(
            'res.users',
            'Prepared By',
            states={'done': [('readonly', True)]},
            help=(
                "Entered automatically by the “last user” who saved it."
                " System generated."
            ),
        ),
        'verified_by_user_id': fields.many2one(
            'res.users',
            'Verified By',
            states={'done': [('readonly', True)]},
            help=(
                "Entered automatically by the “last user”"
                " who saved it. System generated."
            ),
        ),
        'deposit_bag_no': fields.char(
            'Deposit Bag No',
            size=64,
            states={'done': [('readonly', True)]},
            help="Deposit Bag number for courier transit."
        ),
        'bank_tracking_no': fields.char(
            'Deposit Tracking No',
            size=64,
            help=(
                "This field is used to hold a tracking number provided "
                "by the bank/financial institution often used in Remote "
                "Deposit Capture on a deposit receipt. "
                "Entered after deposit occurs."
            ),
        ),
        'move_id': fields.many2one(
            'account.move',
            'Journal Entry',
            readonly=True,
            select=1,
            help="Link to the automatically generated Journal Items."
        ),
        'name': fields.related(
            'move_id',
            'name',
            type='char',
            readonly=True,
            size=64,
            relation='account.move',
            string='Deposit Ticket #',
            help=(
                "Each deposit will have a unique sequence ID. "
                "System generated."
            ),
        ),
        'ticket_line_ids': fields.one2many(
            'deposit.ticket.line',
            'deposit_id',
            'Deposit Ticket Line',
            states={'done': [('readonly', True)]}
        ),
        'amount': fields.function(
            _get_amount,
            method=True,
            string='Amount',
            digits_compute=dp.get_precision('Account'),
            type='float',
            help=(
                "Calculates the Total of All Deposit Lines – "
                "This is the Total Amount of Deposit."
            ),
        ),
        'count_total': fields.function(
            _get_count_total,
            method=True,
            type='float',
            string='Total Items',
            help="Counts the total # of line items in the deposit ticket."
        ),
        'state': fields.selection(
            lambda self, cr, uid, context={}: self.get_deposit_states(
                cr, uid, context=context),
            'State',
            select=True,
            readonly=True
        ),
    }

    _defaults = {
        'state': 'draft',
        'period_id': _get_period,
        'date': time.strftime('%Y-%m-%d'),
        'company_id': (
            lambda self, cr, uid, c:
                self.pool.get('res.users').browse(
                    cr, uid, uid, c
                ).company_id.id
        ),
    }

    # the most recent deposits displays first
    _order = "date desc"

    def add_deposit_items(self, cr, uid, ids, context=None):
        """
        Display the wizard to allow the 'Deposit Preparer'
        to select payments for deposit.
        """
        if context is None:
            context = {}
        return {
            'name': _("Select Payments for Deposit"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'add.deposit.items',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': dict(context, active_ids=ids)
        }
