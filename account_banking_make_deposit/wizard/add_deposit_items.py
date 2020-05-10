# Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
# Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class AddDepositItems(models.TransientModel):
    _name = "add.deposit.items"
    _description = "Add Deposit Items"

    name = fields.Char('Name', size=64)
    deposit_items_line_ids = fields.One2many(
        'deposit.items.line', 'deposit_items_id', 'Lines')

    @api.model
    def default_get(self, field_lines):
        deposit_ticket = self.env['deposit.ticket']
        account_move_line = self.env['account.move.line']
        account_move = self.env['account.move']

        deposits = \
            deposit_ticket.browse(self.env.context.get('active_ids', []))
        res = super(AddDepositItems, self).default_get(field_lines)

        move_lines = []
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
            move_ids = [m.id for m in account_move.search([
                ('state', '=', 'posted')])]

            lines = account_move_line.search([
                ('account_id', '=', deposit.deposit_from_account_id.id),
                ('move_id', 'in', move_ids),
                ('draft_assigned', '=', False),
                ('deposit_id', '=', False)])
            for line in lines:
                vals = {
                    'name': line.name,
                    'ref': line.ref,
                    'amount': line.debit > 0 and line.debit or -line.credit,
                    'partner_id': line.partner_id.id,
                    'date': line.date,
                    'move_line_id': line.id,
                    'company_id': line.company_id.id
                }
                move_lines.append([0, '_', vals])

            if 'deposit_items_line_ids' in field_lines:
                res.update({'deposit_items_line_ids': move_lines})
        return res

    @api.multi
    def select_all(self):
        """Select all the deposit item lines in the wizard."""
        deposit_items_line = self.env['deposit.items.line']
        line_ids = deposit_items_line.search([(
            'deposit_items_id', '=', self.id)])
        line_ids.write({'draft_assigned': True})
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'add.deposit.items',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }

    @api.multi
    def unselect_all(self):
        """Unselect all the deposit item lines in the wizard."""
        deposit_items_line = self.env['deposit.items.line']
        line_ids = deposit_items_line.search([(
            'deposit_items_id', '=', self.id)])
        line_ids.write({'draft_assigned': False})
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'add.deposit.items',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }

    @api.multi
    def add_deposit_lines(self):
        """Add Deposit Items Lines as Deposit Ticket Lines for the deposit."""
        deposit_ticket_id = self._context['active_id']
        account_move_line = self.env['account.move.line']
        deposit_ticket_line = self.env['deposit.ticket.line']

        for add_deposit_item in self:
            # Add the deposit ticket item lines which have
            # 'draft_assigned' checked
            valid_items_line_ids = [
                line for line in add_deposit_item.deposit_items_line_ids
                if line.draft_assigned
            ]
            move_line_ids = []
            for line in valid_items_line_ids:
                # Any Line cannot be manually added.
                # Choose only from the selected lines.
                if not line.move_line_id:
                    raise UserError(_(
                        'You cannot add any new deposit line item '
                        'manually as of this revision!'))

                # Creating but not using the id of the new object anywhere
                deposit_ticket_line.create({
                    'name': line.name,
                    'ref': line.ref,
                    'amount': line.amount,
                    'partner_id': line.partner_id.id,
                    'date': line.date,
                    'move_line_id': line.move_line_id.id,
                    'company_id': line.company_id.id,
                    'deposit_id': deposit_ticket_id,
                })

                move_line_ids.append(line.move_line_id.id)

            account_move_line.browse(move_line_ids).write({
                'draft_assigned': True})
        return {'type': 'ir.actions.act_window_close'}


class DepositItemsLine(models.TransientModel):
    _name = "deposit.items.line"
    _description = "Deposit Items Line"

    name = fields.Char('Name', size=64)
    ref = fields.Char('Reference', size=64)
    partner_id = fields.Many2one('res.partner', 'Partner')
    date = fields.Date('Date', required=True)
    amount = fields.Float('Amount', digits=dp.get_precision('Account'))
    draft_assigned = fields.Boolean('Select')
    deposit_items_id = fields.Many2one('add.deposit.items', 'Deposit Items ID')
    move_line_id = fields.Many2one('account.move.line', 'Journal Item')
    company_id = fields.Many2one('res.company', 'Company')
