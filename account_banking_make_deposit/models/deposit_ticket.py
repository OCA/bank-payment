# Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
# Copyright (C) 2017 Thinkwell Designs (<http://code.compassfoundation.io>)
# Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class DepositTicket(models.Model):
    _name = "deposit.ticket"
    _description = "Deposit Ticket"
    _order = "date desc"

    @api.multi
    def check_group(self):
        """
        Check if following security constraints are implemented for groups:
        Make Deposits Preparer - they can create, view and delete any of the
        Deposit Tickets provided the Deposit Ticket is not in the DONE state,

        or the Ready for Review state.
        Make Deposits Verifier - they can create, view, edit, and delete any
        of the Deposits Tickets information at any time.
        NOTE: DONE Deposit Tickets are only allowed to be deleted by a
        Make Deposits Verifier.
        """

        has_perm = self.user_has_groups(
            'account_banking_make_deposit.group_make_deposits_verifier')

        for deposit in self:
            if deposit.state != 'draft' and not has_perm:
                raise UserError(_(
                    "Only a member of Deposits Verifier group may delete/edit "
                    "deposit tickets when not in draft state!"))
        return True

    @api.multi
    def unlink(self):
        # Check if the user is allowed to perform the action
        self.check_group()
        # Call the method necessary to remove the changes made earlier
        self.remove_all()
        return super(DepositTicket, self).unlink()

    @api.multi
    def write(self, vals):
        # Check if the user is allowed to perform the action
        self.check_group()
        return super(DepositTicket, self).write(vals)

    @api.multi
    def action_cancel(self):
        # Call the method necessary to remove the changes made earlier
        self.remove_all()
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def action_review(self):
        self.write({
            'state': 'to_be_reviewed',
            'prepared_by_user_id': self.env.user.id,
        })
        return True

    @api.multi
    def action_process(self):
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
        for deposit in self:
            if not deposit.journal_id.sequence_id:
                raise UserError(
                    _('Please define sequence on deposit journal')
                )

            # Create the move lines first
            move_lines.append(
                (0, '_', self.get_move_line(deposit, 'src'))
            )
            move_lines.append(
                (0, '_', self.get_move_line(deposit, 'dest'))
            )
            # Create the move for the deposit
            move = {
                'ref': deposit.deposit_bag_no,
                'name': '/',
                'line_ids': move_lines,
                'journal_id': deposit.journal_id.id,
                'date': deposit.date,
                'narration': deposit.deposit_bag_no,
                'deposit_id': deposit.id,
            }
            move_id = self.env['account.move'].create(move)
            # Post the account move
            move_id.post()
            # Link the move with the deposit and populate other fields
            self.write({
                'move_id': move_id.id,
                'state': 'done',
                'verified_by_user_id': self.env.user.id,
                'verified_date': fields.Date.today(),
            })

        return True

    @api.multi
    def get_move_line(self, deposit, line_type):
        return {
            'type': line_type,
            'name': deposit.name or '/',
            'debit': line_type == 'dest' and deposit.amount or 0.0,
            'credit': line_type == 'src' and deposit.amount or 0.0,
            'account_id': (
                line_type == 'src' and
                deposit.deposit_from_account_id.id or
                deposit.deposit_to_account_id.id
            ),
            'date': deposit.date,
            'ref': deposit.deposit_bag_no or '',
            'deposit_id': deposit.id,
        }

    @api.multi
    def remove_all(self):
        """
        Reset the deposit ticket to draft state,
        and remove the entries associated with the DONE transactions (
        account moves, updating account.move.lines, resetting preparer
        and verifier and verified date fields.
        Reflect all changes necessary.
        """
        vals = {
            'draft_assigned': False,
            'deposit_id': False
        }
        for deposit in self:
            for move_line in deposit.move_id:
                move_line.write(vals)

            deposit.move_id.button_cancel()
            deposit.move_id.unlink()

        return True

    @api.multi
    def action_cancel_draft(self):
        # Call the method necessary to remove the changes made earlier
        self.remove_all()
        self.write({
            'state': 'draft',
            'verified_by_user_id': False,
            'verified_date': False,
            'prepared_by_user_id': False
        })
        return True

    @api.multi
    def _compute_amount(self):
        for deposit in self:
            total = 0.0
            for line in deposit.ticket_line_ids:
                total += line.amount
            deposit.amount = total
            deposit.count_total = len(deposit.ticket_line_ids)

    name = fields.Char(
        'Deposit Ticket #', related='move_id.name', index=1,
        help=(
            "Each deposit will have a unique sequence ID. "
            "System generated."
        ),
    )
    memo = fields.Char(
        'Memo', size=64,
        states={'done': [('readonly', True)]},
        help="Memo for the deposit ticket"
    )
    deposit_to_account_id = fields.Many2one(
        'account.account', 'Deposit To Acct', required=True,
        states={'done': [('readonly', True)]},
        domain="[('company_id', '=', company_id)]",
        help="The Bank/Gl Account the Deposit is being made to.",
    )
    deposit_from_account_id = fields.Many2one(
        'account.account', 'Deposit From Acct', required=True,
        states={'done': [('readonly', True)]},
        domain="[('company_id', '=', company_id)]",
        help="The Bank/GL Account the Payments are currently found in.",
    )
    date = fields.Date(
        'Date of Deposit', required=True, default=fields.Date.today(),
        states={'done': [('readonly', True)]},
        help="The Date of the Deposit Ticket.",
    )
    journal_id = fields.Many2one(
        'account.journal', 'Journal', required=True,
        states={'done': [('readonly', True)]},
        help="The Journal to hold accounting entries.",
    )
    company_id = fields.Many2one(
        'res.company', 'Company', required=True, readonly=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'account.account'),
        help="The Company for which the deposit ticket is made",
    )
    deposit_method_id = fields.Many2one(
        'deposit.method', 'Deposit Method',
        states={'done': [('readonly', True)]},
        help=(
            "This is how the deposit was made:\nExamples:\n"
            "* Teller \n"
            "* ATM \n"
            "* Remote Deposit Capture \n"
            "* Online Deposit Capture \n"
            "* Night Drop \n"
            "* Armored Vehicle"
        )
    )
    verified_date = fields.Date(
        'Verified Date',
        states={'done': [('readonly', True)]},
        help="Date in which Deposit Ticket was verified.",
    )
    prepared_by_user_id = fields.Many2one(
        'res.users', 'Prepared By',
        states={'done': [('readonly', True)]},
        help=(
            "Entered automatically by the 'last user' who saved it."
            " System generated."
        ),
    )
    verified_by_user_id = fields.Many2one(
        'res.users', 'Verified By',
        states={'done': [('readonly', True)]},
        help=(
            "Entered automatically by the 'last user'"
            " who saved it. System generated."
        ),
    )
    deposit_bag_no = fields.Char(
        'Deposit Bag #', size=64,
        states={'done': [('readonly', True)]},
        help="Deposit Bag number for courier transit.",
    )
    bank_tracking_no = fields.Char(
        'Deposit Tracking #', size=64,
        help=(
            "This field is used to hold a tracking number provided "
            "by the bank/financial institution often used in Remote "
            "Deposit Capture on a deposit receipt. "
            "Entered after deposit occurs."
        ),
    )
    move_id = fields.Many2one(
        'account.move', 'Journal Entry',
        readonly=True, index=True,
        help="Link to the automatically generated Journal Items.",
    )
    ticket_line_ids = fields.One2many(
        'deposit.ticket.line', 'deposit_id',
        'Deposit Ticket Line',
        states={'done': [('readonly', True)]},
    )
    amount = fields.Float(
        'Amount', compute='_compute_amount',
        digits=dp.get_precision('Account'),
        help=(
            "Calculates the Total of All Deposit Lines - "
            "This is the Total Amount of Deposit."
        ),
    )
    count_total = fields.Float(
        'Total Items', compute='_compute_amount',
        help="Counts the total # of line items in the deposit ticket."
    )
    state = fields.Selection(
        [
            ('draft', _('Draft')),
            ('to_be_reviewed', _('Ready for Review')),
            ('done', _('Done')),
            ('cancel', _('Cancel')),
        ],
        'State', index=True, readonly=True, default='draft'
    )

    @api.multi
    def add_deposit_items(self):
        """
        Display the wizard to allow the 'Deposit Preparer'
        to select payments for deposit.
        """
        return {
            'name': _("Select Payments for Deposit"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'add.deposit.items',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }

    @api.onchange('journal_id')
    def onchange_journal(self):
        for rec in self:
            if rec.journal_id:
                rec.deposit_to_account_id = \
                    rec.journal_id.default_debit_account_id.id

    @api.multi
    def _get_report_base_filename(self):
        self.ensure_one()
        return self.state == 'draft' and _('Draft_Deposit_Ticket') or \
            self.state == 'to_be_reviewed' and _('Deposit_Ticket') or \
            self.state == 'done' and _('Deposit_Ticket_%s') % (self.name)
